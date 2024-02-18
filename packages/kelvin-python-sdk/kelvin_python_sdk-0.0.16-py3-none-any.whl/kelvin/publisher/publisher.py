from __future__ import annotations

import asyncio
import csv
import random
from abc import ABC, abstractmethod
from asyncio import Queue, StreamReader, StreamWriter
from datetime import datetime, timedelta
from typing import AsyncGenerator, Callable, Dict, List, Optional, Tuple, Union

import arrow
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from kelvin.application.stream import KelvinStreamConfig
from kelvin.message import (
    KRN,
    KMessageType,
    KMessageTypeControl,
    KMessageTypeData,
    KMessageTypeParameter,
    KMessageTypeRecommendation,
    KRNAssetDataStream,
    KRNAssetParameter,
    KRNWorkloadAppVersion,
    Message,
)
from kelvin.message.base_messages import (
    ManifestDatastream,
    Resource,
    ResourceDatastream,
    RuntimeManifest,
    RuntimeManifestPayload,
)
from kelvin.publisher.config import AppConfig, AssetsEntry, Metric, ParameterDefinition


class PublisherError(Exception):
    pass


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    items: list = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class PublishServer:
    CYCLE_TIMEOUT_S = 0.25
    NODE = "test_node"
    WORKLOAD = "test_workload"

    app_config: AppConfig
    allowed_assets: Optional[list[str]] = None
    asset_params: dict[Tuple[str, str], Union[bool, float, str]] = {}

    on_message: Callable[[Message], None]
    write_queue: Queue[Message]

    def __init__(self, conf: AppConfig, generator: DataGenerator) -> None:
        self.app_config = conf
        if self.app_config.app.kelvin.assets:
            self.allowed_assets = [asset.name for asset in self.app_config.app.kelvin.assets]

        self.writer = None
        self.on_message = log_message
        self.write_queue = Queue()
        self.host = "127.0.0.1"
        self.port = KelvinStreamConfig().port
        self.running = False
        self.generator = generator

    def update_param(self, asset: str, param: str, value: Union[bool, float, str]) -> None:
        """Sets an asset parameter.
        Empty asset ("") to change app default

        Args:
            asset (Optional[str]): asset name (empty ("") for fallback)
            param (str): param name
            value (Union[bool, float, str]): param value
        """
        self.asset_params[(asset, param)] = value

    def add_extra_assets(self, assets_extra: list[str]) -> None:
        self.allowed_assets = assets_extra

    def build_config_message(self) -> RuntimeManifest:
        # Prepare app parameters
        resources: List[Resource] = []
        datastreams: List[ManifestDatastream] = []
        configuration = {}

        if self.app_config.app.type == "bridge":
            configuration = self.app_config.app.bridge.configuration

            asset_metrics_map: dict[str, Resource] = {}
            metric_datastream_map: dict[str, ManifestDatastream] = {}
            for metric in self.app_config.app.bridge.metrics_map:
                resource = asset_metrics_map.setdefault(
                    metric.asset_name, Resource(type="asset", name=metric.asset_name)
                )

                resource.datastreams[metric.name] = ResourceDatastream(
                    map_to=metric.name, access=metric.access, owned=True, configuration=metric.configuration
                )

                metric_datastream_map.setdefault(
                    metric.name, ManifestDatastream(name=metric.name, primitive_type_name=metric.data_type)
                )

            resources = list(asset_metrics_map.values())
            datastreams = list(metric_datastream_map.values())

        elif self.app_config.app.type == "kelvin":
            configuration = self.app_config.app.kelvin.configuration

            # Prepare asset parameters
            # Parameter priority: asset override > override default > asset param on app config > default on app config
            for asset_name in self.allowed_assets or []:
                asset_params = {}
                for param in self.app_config.app.kelvin.parameters:
                    payload = (
                        self.asset_params.get((asset_name, param.name))  # asset override
                        or self.asset_params.get(("", param.name))  # asset override default ("")
                        or next(  # asset parameter defined in configuration
                            (
                                asset.parameters.get(param.name, {}).get("value")
                                for asset in self.app_config.app.kelvin.assets
                                if asset.name == asset_name
                            ),
                            None,
                        )
                        or param.default.get("value", None)  # app defaults
                        if param.default
                        else None
                    )

                    if payload is None:
                        # asset has no parameter and parameter doesn't have default value
                        continue

                    try:
                        if param.data_type == "number":
                            payload = float(payload)
                        elif param.data_type == "string":
                            payload = str(payload)
                        elif param.data_type == "boolean":
                            payload = str(payload).lower() in ["true", "1"]
                    except ValueError:
                        continue

                    asset_params[param.name] = payload

                asset_properties: Dict = next(
                    (asset.properties for asset in self.app_config.app.kelvin.assets if asset.name == asset_name), {}
                )

                resources.append(
                    Resource(type="asset", name=asset_name, parameters=asset_params, properties=asset_properties)
                )

        return RuntimeManifest(
            resource=KRNWorkloadAppVersion(
                node=self.NODE,
                workload=self.WORKLOAD,
                app=self.app_config.info.name,
                version=self.app_config.info.version,
            ),
            payload=RuntimeManifestPayload(resources=resources, configuration=configuration, datastreams=datastreams),
        )

    async def start_server(self) -> None:
        server = await asyncio.start_server(self.new_client, self.host, self.port)
        print("Publisher started.")

        async with server:
            await server.serve_forever()

    async def new_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        if self.running is True:
            writer.close()
            return

        print("Connected")
        self.running = True

        connection_tasks = {
            asyncio.create_task(self.handle_read(reader)),
            asyncio.create_task(self.handle_write(writer, self.write_queue)),
        }

        gen_task = asyncio.create_task(self.handle_generator(self.generator))

        config_msg = self.build_config_message()
        writer.write(config_msg.encode() + b"\n")
        try:
            await writer.drain()
        except ConnectionResetError:
            pass

        _, pending = await asyncio.wait(connection_tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

        if not task.done():
            gen_task.cancel()

        self.running = False
        print("Disconnected")

    async def handle_read(self, reader: StreamReader) -> None:
        while self.running:
            data = await reader.readline()
            if not len(data):
                break
            try:
                msg = Message.parse_raw(data)
                self.on_message(msg)
            except Exception as e:
                print("error parsing message", e)

    async def handle_write(self, writer: StreamWriter, queue: Queue[Message]) -> None:
        while self.running and not writer.is_closing():
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=self.CYCLE_TIMEOUT_S)
            except asyncio.TimeoutError:
                continue

            writer.write(msg.encode() + b"\n")

            try:
                await writer.drain()
            except ConnectionResetError:
                pass

    async def handle_generator(self, generator: DataGenerator) -> None:
        async for data in generator.run():
            await self.publish_data(data)

    async def publish_unsafe(self, msg: Message) -> None:
        """Publish the message as is, do not validate it against the app configuration

        Args:
            msg (Message): message to publish
        """
        await self.write_queue.put(msg)

    async def publish_data(self, data: MessageData) -> bool:
        if self.allowed_assets is not None and len(data.asset) > 0 and data.asset not in self.allowed_assets:
            print(f"error publishing: asset not allowed to app. asset={data.asset}")
            return False

        # if data.asset is empty publish to all allowed_assets (if set)
        assets = [data.asset] if len(data.asset) > 0 else self.allowed_assets
        if assets is None:
            print("error publishing to empty asset: no allowed assets set")
            return False

        app_resource: Union[Metric, ParameterDefinition, None] = None
        msg_resource_builder: Optional[type[KRN]] = None
        try:
            # check is app input
            app_resource = next(i for i in self.app_config.app.kelvin.inputs if i.name == data.resource)
            msg_type: KMessageType = KMessageTypeData(primitive=app_resource.data_type)
            msg_resource_builder = KRNAssetDataStream
        except StopIteration:
            try:
                # check is app param
                app_resource = next(p for p in self.app_config.app.kelvin.parameters if p.name == data.resource)
                msg_type = KMessageTypeParameter(primitive=app_resource.data_type)
                msg_resource_builder = KRNAssetParameter
            except StopIteration:
                app_resource = None

        if app_resource is None or msg_resource_builder is None:
            # invalid resource for this app
            print(f"error publishing: invalid resource to app. asset={data.asset} resource={data.resource}")
            return False

        for asset in assets:
            try:
                msg = Message(
                    type=msg_type,
                    timestamp=data.timestamp or datetime.now().astimezone(),
                    resource=msg_resource_builder(asset, data.resource),
                    payload=data.value,
                )

                await self.write_queue.put(msg)
            except ValidationError:
                print(
                    f"error publishing value: invalid value for resource. resource={data.resource}, value={data.value}"
                )
        return True


def log_message(msg: Message) -> None:
    msg_log = ""
    if isinstance(msg.type, KMessageTypeData):
        msg_log = "Data "
    elif isinstance(msg.type, KMessageTypeControl):
        msg_log = "Control Change "
    elif isinstance(msg.type, KMessageTypeRecommendation):
        msg_log = "Recommendation "

    print(f"\nReceived {msg_log}Message:\n", repr(msg))


@dataclass
class MessageData:
    asset: str
    resource: str
    timestamp: Optional[datetime]
    value: Union[bool, float, str]


class DataGenerator(ABC):
    @abstractmethod
    async def run(self) -> AsyncGenerator[MessageData, None]:
        if False:
            yield  # trick for mypy


class CSVPublisher(DataGenerator):
    DEFAULT_PERIOD = 1

    def __init__(self, csv_file_path: str, period: Optional[float], offset_timestamps: bool = False):
        self.period = period
        self.offset_timestamps = offset_timestamps
        self.csv_file_path = csv_file_path
        self.offset: timedelta = timedelta(0)

    def parse_timestamp(self, ts_str: str, offset: timedelta = timedelta(0)) -> Optional[datetime]:
        try:
            timestamp = float(ts_str)
            return arrow.get(timestamp).datetime + offset
        except ValueError:
            pass

        try:
            return arrow.get(ts_str).datetime + offset
        except Exception as e:
            print(f"csv: error parsing timestamp, skipping value. timestamp={ts_str}", e)
            return None

    @property
    def realtime_publish(self) -> bool:
        return self.period is None

    async def run(self) -> AsyncGenerator[MessageData, None]:
        self.csv_file = open(self.csv_file_path)
        self.csv_reader = csv.reader(self.csv_file)
        self.headers = next(self.csv_reader)
        last_timestamp = datetime(year=9999, month=12, day=31)

        if "timestamp" not in self.headers:
            # realtime publish is not possible if csv has no timestamp
            self.period = self.period if self.period is not None else self.DEFAULT_PERIOD
            if self.offset_timestamps:
                print(
                    f"csv error: offset-timestamps is set but csv has no timestamps. setting period to {self.period}s"
                )
            self.offset_timestamps = False

        if self.offset_timestamps:
            row = next(self.csv_reader)
            row_dict = dict(zip(self.headers, row))

            asset = row_dict.pop("asset", "")
            ts_str = row_dict.pop("timestamp")

            ts = self.parse_timestamp(ts_str)
            if ts is not None:
                self.offset = datetime.now().astimezone() - ts.astimezone()
                ts = ts + self.offset
                last_timestamp = ts

                for r, v in row_dict.items():
                    yield MessageData(asset=asset, resource=r, value=v, timestamp=ts)

        for row in self.csv_reader:
            row_dict = dict(zip(self.headers, row))

            asset = row_dict.pop("asset", "")
            ts_str = row_dict.pop("timestamp", "")
            row_timestamp = None
            if ts_str != "":
                row_timestamp = self.parse_timestamp(ts_str, self.offset)
                if row_timestamp is None:
                    continue

            if self.realtime_publish and row_timestamp is not None:
                # real timestamps
                wait_time = max((row_timestamp.astimezone() - last_timestamp.astimezone()).total_seconds(), 0)
                await asyncio.sleep(wait_time)

            # if a row as no timestamp set a huge timestamp so it can't sleep forever next iteration
            last_timestamp = row_timestamp or datetime(year=9999, month=12, day=31)

            for r, v in row_dict.items():
                yield MessageData(asset=asset, resource=r, value=v, timestamp=row_timestamp)

            if not self.realtime_publish:
                # wait period if not realtime publish
                await asyncio.sleep(self.period)  # type: ignore

        print("\nCSV ingestion is complete")


class Simulator(DataGenerator):
    app_yaml: str
    app_config: AppConfig
    rand_min: float
    rand_max: float
    random: bool
    current_value: float
    assets: list[AssetsEntry]
    params_override: dict[str, Union[bool, float, str]]

    def __init__(
        self,
        app_config: AppConfig,
        period: float,
        rand_min: float = 0,
        rand_max: float = 100,
        random: bool = True,
        assets_extra: list[str] = [],
        parameters_override: list[str] = [],
    ):
        self.app_config = app_config
        self.period = period
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.random = random
        self.current_value = self.rand_min - 1
        self.params_override: dict[str, Union[bool, float, str]] = {}

        for override in parameters_override:
            param, value = override.split("=", 1)
            self.params_override[param] = value

        if len(assets_extra) > 0:
            self.assets = [AssetsEntry(name=asset, parameters={}) for asset in assets_extra]
        elif self.app_config.app.kelvin.assets:
            self.assets = self.app_config.app.kelvin.assets
        else:
            raise PublisherError("No assets set")

    def generate_random_value(self, data_type: str) -> Union[bool, float, str]:
        if data_type == "boolean":
            return random.choice([True, False])

        if self.random:
            number = round(random.random() * (self.rand_max - self.rand_min) + self.rand_min, 2)
        else:
            if self.current_value >= self.rand_max:
                self.current_value = self.rand_min
            else:
                self.current_value += 1
            number = self.current_value

        if data_type == "number":
            return number

        # if data_type == "string":
        return f"str_{number}"

    async def run(self) -> AsyncGenerator[MessageData, None]:
        while True:
            for input in self.app_config.app.kelvin.inputs:
                for asset in self.assets:
                    yield MessageData(
                        asset=asset.name,
                        resource=input.name,
                        value=self.generate_random_value(input.data_type),
                        timestamp=None,
                    )

            await asyncio.sleep(self.period)
