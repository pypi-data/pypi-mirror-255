from __future__ import annotations

import asyncio
from asyncio import Event, Queue
from types import TracebackType
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Optional, Tuple, Type, TypeVar, Union

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import Literal, Self, TypeAlias

from kelvin.application import filters
from kelvin.application.stream import KelvinStream, KelvinStreamConfig
from kelvin.logs import configure_logger, logger
from kelvin.message import KRNAsset, KRNAssetParameter, KRNParameter, Message
from kelvin.message.base_messages import ManifestDatastream, Resource, RuntimeManifest
from kelvin.message.msg_builders import MessageBuilder

NoneCallbackType: TypeAlias = Optional[Callable[..., Awaitable[None]]]
MessageCallbackType: TypeAlias = Optional[Callable[[Message], Awaitable[None]]]

E = TypeVar("E", bound=Exception)


@dataclass
class AssetInfo:
    name: str
    properties: Dict[str, Union[bool, float, str]] = Field(default_factory=dict)
    parameters: Dict[str, Union[bool, float, str]] = Field(default_factory=dict)


@dataclass
class Datastream:
    name: str
    type: str
    unit: Optional[str] = None


@dataclass
class ResourceDatastream:
    asset: KRNAsset
    datastream: Datastream
    access: Literal["RO", "RW", "WO"] = "RO"
    configuration: Dict = Field(default_factory=dict)


class KelvinApp:
    """Kelvin Client to connect to the Application Stream.
    Use this class to connect and interface with the Kelvin Stream.

    After connecting, the connection is handled automatically in the background.

    Use filters or filter_stream to easily listen for specific messages.
    Use register_callback methods to register callbacks for events like connect and disconnect.
    """

    READ_CYCLE_TIMEOUT_S = 0.25
    RECONNECT_TIMEOUT_S = 3

    def __init__(self, config: KelvinStreamConfig = KelvinStreamConfig()) -> None:
        self._stream = KelvinStream(config)
        self._filters: list[Tuple[Queue, filters.KelvinFilterType]] = []
        self._conn_task: Optional[asyncio.Task] = None

        # map of asset name to map of parameter name to parameter message
        self._assets: dict[str, AssetInfo] = {}
        # dict with the same structure as the configuration defined by the app
        self._app_configuration: dict = {}
        self._resources_list: list = []

        self.on_connect: NoneCallbackType = None
        self.on_disconnect: NoneCallbackType = None

        self.on_message: MessageCallbackType = None
        self.on_asset_input: MessageCallbackType = None
        self.on_control_change: MessageCallbackType = None

        self.on_asset_parameter: MessageCallbackType = None
        self.on_app_configuration: MessageCallbackType = None

        self._config_received = Event()

        configure_logger()

    async def connect(self) -> None:
        """Establishes a connection to Kelvin Stream.

        This method will wait until the connection is successfully established, and the application is ready to run
        with its initial configuration. If you prefer not to block and want the application to continue execution,
        consider using asyncio.wait_for() with a timeout.
        """
        self._is_to_connect = True
        self._conn_task = asyncio.create_task(self._handle_connection())
        await self.config_received.wait()

    async def disconnect(self) -> None:
        """Disconnects from Kelvin Stream"""
        self._is_to_connect = False
        if self._conn_task:
            await self._conn_task
        await self._stream.disconnect()

    @property
    def assets(self) -> dict[str, AssetInfo]:
        """Assets
        A dict containing the parameters of each asset configured to this application.
        This dict is automatically updated when the application receives parameter updates.
        eg:
        {
            "asset1": AssetInfo(
                name="asset1",
                properties={
                    "tubing_length": 25.0,
                    "area": 11.0
                },
                parameters={
                    "param-bool": False,
                    "param-number": 7.5,
                    "param-string": "hello",
                },
            )
        }

        Returns:
            dict[str, AssetInfo]: the dict of the asset parameters
        """

        return self._assets

    @property
    def app_configuration(self) -> dict:
        """App configuration
        A dict containing the app parameters with the same structure defined in the app.yaml
        eg:
        {
            "foo": {
                "conf_string": "value1",
                "conf_number": 25,
                "conf_bool": False,
            }
        }
        Returns:
            dict: the dict with the app configuration
        """
        return self._app_configuration

    @property
    def resources_map(self) -> list[ResourceDatastream]:
        """Resources Map for the application
        A list of all resources configured to the application

        Returns:
            list[ResourceDatastream]: list of resources
        """
        return self._resources_list

    @property
    def config_received(self) -> Event:
        """An asyncio Event that is set when the application receives it's initial configuration
        When the application connects it receives a initial configuration to set the initial app and asset parameters.
        If the application really depends on them this event can be waited (await cli.config_received.wait()) to make
        sure the configuration is available before continuing.

        Returns:
            Event: an awaitable asyncio.Event for the initial app configuration
        """
        return self._config_received

    async def __aenter__(self) -> Self:
        """Enter the connection."""

        await self.connect()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[E]],
        exc_value: Optional[E],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit the connection."""

        try:
            await self.disconnect()
        except Exception:
            pass

        return None

    async def _handle_connection(self) -> None:
        while self._is_to_connect:
            try:
                try:
                    await self._stream.connect()
                except ConnectionError:
                    logger.error(f"Error connecting, reconnecting in {self.RECONNECT_TIMEOUT_S} sec.")
                    await asyncio.sleep(self.RECONNECT_TIMEOUT_S)
                    continue

                if self.on_connect:
                    await self.on_connect()

                await self._handle_read()

                if self.on_disconnect:
                    await self.on_disconnect()
            except Exception:
                logger.exception("Unexpected error on connection handler")
                await asyncio.sleep(self.RECONNECT_TIMEOUT_S)

    async def _handle_read(self) -> None:
        while self._is_to_connect:
            try:
                msg = await self._stream.read()
            except ConnectionError:
                logger.exception("Connection error")
                break

            await self._process_message(msg)

            self._route_to_filters(msg)

    def _msg_is_control_change(self, msg: Message) -> bool:
        # todo: implement when we know how to check if the message is control changes
        # we need the app configuration to know this
        return False

    def _update_app_configuration_map(self, key: str, value: Any) -> None:
        # Unflatten the parameter name from the nested a.b.c to a dict of {a: {b: {c: msg}}}
        self._app_configuration = expand_map(self._app_configuration, build_nested_map(key, value))

    def _update_assets_map(self, asset: str, param: str, value: Any) -> None:
        self._assets.setdefault(asset, AssetInfo(asset)).parameters[param] = value

    def _setup_parameters(self, resources: list[Resource]) -> None:
        for resource in resources:
            if resource.type == "asset":
                self._assets[resource.name] = AssetInfo(  # type: ignore
                    name=resource.name, properties=resource.properties, parameters=resource.parameters  # type: ignore
                )
            elif resource.type == "app":
                for param, value in resource.parameters.items():
                    self._update_app_configuration_map(key=param, value=value)

    def _setup_resources_map(self, resources: list[Resource], datastreams: list[ManifestDatastream]) -> None:
        self._resources_list = []

        for resource in resources:
            if resource.type != "asset":
                continue

            for ds_name, datastream in resource.datastreams.items():
                manif_ds = next((ds for ds in datastreams if ds.name == ds_name), None)
                if manif_ds is None:
                    logger.warning("resource datastream not defined in manifest datatreams", datastream=ds_name)
                    continue

                name = datastream.map_to if datastream.map_to else ds_name

                self._resources_list.append(
                    ResourceDatastream(
                        asset=KRNAsset(resource.name),  # type: ignore
                        access=datastream.access,
                        configuration=datastream.configuration,
                        datastream=Datastream(
                            name=name, type=manif_ds.primitive_type_name, unit=manif_ds.unit_name  # type: ignore
                        ),
                    )
                )

    async def _process_message(self, msg: Message) -> None:
        if isinstance(msg, RuntimeManifest):
            self._setup_parameters(msg.payload.resources)
            self._setup_resources_map(msg.payload.resources, msg.payload.datastreams)
            self._app_configuration = msg.payload.configuration
            self._config_received.set()

        if self.on_message:
            await self.on_message(msg)

        if filters.is_parameter(msg):
            # determine if it's an asset or app parameter and store it
            if isinstance(msg.resource, KRNAssetParameter):
                self._update_assets_map(msg.resource.asset, msg.resource.parameter, msg.payload)
                if self.on_asset_parameter:
                    await self.on_asset_parameter(msg)
            elif isinstance(msg.resource, KRNParameter):
                self._update_app_configuration_map(msg.resource.parameter, msg.payload)
                if self.on_app_configuration:
                    await self.on_app_configuration(msg)
            return

        if self.on_control_change and self._msg_is_control_change(msg):
            await self.on_control_change(msg)
            return

        if self.on_asset_input and filters.is_asset_data_message(msg):
            await self.on_asset_input(msg)
            return

    def _route_to_filters(self, msg: Message) -> None:
        for queue, func in self._filters:
            if func(msg) is True:
                # todo: check if the message is reference
                queue.put_nowait(msg)

    def filter(self, func: filters.KelvinFilterType) -> Queue[Message]:
        """Creates a filter for the received Kelvin Messages based on a filter function.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            Queue[Message]: Returns a asyncio queue to receive the filtered messages.
        """
        queue: Queue = Queue()
        self._filters.append((queue, func))
        return queue

    def stream_filter(self, func: filters.KelvinFilterType) -> AsyncGenerator[Message, None]:
        """Creates a stream for the received Kelvin Messages based on a filter function.
        See filter.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            AsyncGenerator[Message, None]: Async Generator that can be async iterated to receive filtered messages.

        Yields:
            Iterator[AsyncGenerator[Message, None]]: Yields the filtered messages.
        """
        queue = self.filter(func)

        async def _generator() -> AsyncGenerator[Message, None]:
            while True:
                msg = await queue.get()
                yield msg

        return _generator()

    async def publish(self, msg: Union[Message, MessageBuilder]) -> bool:
        """Publishes a Message to Kelvin Stream

        Args:
            msg (Message): Kelvin Message to publish

        Returns:
            bool: True if the message was sent with success.
        """
        try:
            if isinstance(msg, MessageBuilder):
                m = msg.to_message()
            else:
                m = msg

            return await self._stream.write(m)
        except ConnectionError:
            logger.error("Failed to publish message, connection is unavailable.")
            return False


def build_nested_map(key: str, value: Any) -> dict[str, Any]:
    # build_nested_map takes in a dot-delimited key and returns a nested dictionary
    n = key.split(".")
    ret: dict[str, Any] = {}
    ref = ret
    for i in range(len(n)):
        if i == len(n) - 1:  # terminate - update the last key with the message
            ref[n[i]] = value
        else:
            # if the key doesn't exist, create a new dictionary
            ref[n[i]] = ref.get(n[i], {})

        # update the reference to the next level
        ref = ref[n[i]]
    return ret


def expand_map(entry: dict[str, Any], expansion: dict[str, Any]) -> dict[str, Any]:
    # expand_map takes an existing dictionary (such as {a: {b: {c: msg}}}) and expands it with the new dictionary
    # (such as {a: {b: {d: msg}}}) to produce {a: {b: {c: msg, d: msg}}}
    ref = expansion.copy()
    if entry:
        for key, value in ref.items():
            if key in entry:
                if isinstance(entry[key], dict):
                    entry.update({key: expand_map(entry[key], value)})
                else:
                    entry[key] = expansion[key]
            else:
                entry[key] = value
        return entry
    else:
        return expansion
