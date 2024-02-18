from __future__ import annotations

import asyncio
from typing import Optional

import yaml
from pydantic import BaseModel

from kelvin.application import KelvinApp
from kelvin.logs import logger
from kelvin.message import Boolean, KRNAssetDataStream, Message, Number, String
from kelvin.publisher.publisher import AppConfig, CSVPublisher, MessageData

CONFIG_FILE_PATH = "csv_publisher.yaml"


def message_from_message_data(data: MessageData, outputs: list) -> Optional[Message]:
    output = next((output for output in outputs if output["name"] == data.resource), None)
    if output is None:
        logger.error("csv metric not found in outputs", metric=data.resource)
        return None

    data_type = output.get("data_type")
    if data_type == "boolean":
        msg_type = Boolean
    elif data_type == "number":
        msg_type = Number
    elif data_type == "string":
        msg_type = String
    else:
        return None

    return msg_type(resource=KRNAssetDataStream(data.asset, data.resource), payload=data.value)


class AppConfiguration(BaseModel):
    class Config:
        extra = "allow"

    csv: str
    period: float
    offset_timestamps: bool


async def main() -> None:
    with open(CONFIG_FILE_PATH) as f:
        config_yaml = yaml.safe_load(f)
        config = AppConfig.parse_obj(config_yaml)
        outputs = config.app.kelvin.outputs

    app = KelvinApp()
    await app.connect()

    assets = list(app.assets.keys())

    custom_config = AppConfiguration.parse_obj(app.app_configuration)

    publisher = CSVPublisher(custom_config.csv, custom_config.period, custom_config.offset_timestamps)

    async for data in publisher.run():
        for asset in assets:
            data.asset = asset
            msg = message_from_message_data(data, outputs)
            if msg is not None:
                await app.publish(msg)


if __name__ == "__main__":
    asyncio.run(main())
