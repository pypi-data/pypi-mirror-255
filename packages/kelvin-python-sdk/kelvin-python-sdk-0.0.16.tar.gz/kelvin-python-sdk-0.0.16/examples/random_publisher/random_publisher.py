import asyncio
import random
from typing import Optional

from pydantic import BaseModel

from kelvin.application import KelvinApp
from kelvin.application.client import ResourceDatastream
from kelvin.logs import logger
from kelvin.message import Boolean, KRNAssetDataStream, Message, Number, String


class Config(BaseModel):
    class Config:
        extra = "allow"

    period: float = 30
    min: float = 0
    max: float = 100
    random: bool = True


class RandomPublisher:
    app: KelvinApp
    config: Config
    msg_count: int
    metrics: list[ResourceDatastream]
    current_value: int

    def __init__(self, app=KelvinApp()):
        self.app = app
        self.config = Config()
        self.msg_count = 0
        self.metrics = []
        self.current_value = 0

    async def connect(self):
        await self.app.connect()
        logger.debug(
            "App connected",
            config=self.app.app_configuration,
            assets=self.app.assets,
            resources_map=self.app.resources_map,
        )
        self.config = Config.parse_obj(self.app.app_configuration)
        self.metrics = self.app.resources_map
        self.current_value = self.config.min

    def increment_current_value(self):
        if self.current_value >= self.config.max:
            self.current_value = self.config.min
        else:
            self.current_value += 1

    def build_message_from_resource(self, resource: ResourceDatastream) -> Optional[Message]:
        krn_ad = KRNAssetDataStream(resource.asset.asset, resource.datastream.name)

        if resource.datastream.type == "boolean":
            return Boolean(resource=krn_ad, payload=random.choice([True, False]))

        number = (
            round(random.random() * (self.config.max - self.config.min) + self.config.min, 2)
            if self.config.random
            else self.current_value
        )

        if resource.datastream.type == "number":
            return Number(resource=krn_ad, payload=number)

        if resource.datastream.type == "string":
            return String(resource=krn_ad, payload=f"str_{number}")

        return None

    async def publisher(self) -> None:
        while True:
            for metric in self.metrics:
                msg = self.build_message_from_resource(metric)
                if msg is not None:
                    ok = await self.app.publish(msg)
                    self.msg_count += int(ok)

            self.increment_current_value()
            await asyncio.sleep(self.config.period)

    async def publish_count_log(self) -> None:
        while True:
            logger.info(f"Published {self.msg_count} messages in the last minute")
            self.msg_count = 0
            await asyncio.sleep(60)

    async def run_forever(self):
        await self.connect()

        t = {asyncio.create_task(self.publisher()), asyncio.create_task(self.publish_count_log())}

        await asyncio.gather(*t)


if __name__ == "__main__":
    app = RandomPublisher()
    asyncio.run(app.run_forever())
