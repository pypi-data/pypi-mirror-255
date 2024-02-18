from __future__ import annotations

import asyncio
import random
from asyncio import Queue
from datetime import datetime, timedelta

from kelvin.application import KelvinApp, filters
from kelvin.logs import logger
from kelvin.message import Boolean, ControlChange, KRNAsset, KRNAssetDataStream, Message, Number, Recommendation, String


async def on_connect() -> None:
    print("Hello, it's connected")


async def on_disconnect() -> None:
    print("Hello, it's disconnected")


# Takes Data Messages from KRNAssetDataStream("asset1", "input-number"), doubles its value and publishes it as "output-number"
async def double_msg_value(app: KelvinApp, queue: Queue[Number]) -> None:
    while True:
        msg = await queue.get()
        print("Received Input: ", msg)

        # Publish Data (Number)
        await app.publish(
            Number(resource=KRNAssetDataStream(msg.resource.asset, "output-number"), payload=msg.payload * 2)
        )


async def log_parameters(queue: Queue[Message]) -> None:
    while True:
        msg = await queue.get()

        print("Receive parameter: ", msg)


async def main() -> None:
    logger.info("Hello before configure")

    # Creating instance of Kelvin App Client
    app = KelvinApp()

    logger.info("Hello after configure")
    # Setting Basic App Client Callbacks
    app.on_connect = on_connect
    app.on_disconnect = on_disconnect

    # Creating a filter for a specific resource (krn)
    my_message_filter = app.filter(filters.input_equals("input-number"))
    # Creating async task handling the data filtered above ^
    t1 = asyncio.create_task(double_msg_value(app, my_message_filter))

    # Creating a filter for parameter messages
    my_parameter_filter = app.filter(filters.is_parameter)
    # Creating async task handling the parameter messages filters above ^
    t2 = asyncio.create_task(log_parameters(my_parameter_filter))
    # Connect the App Client
    await app.connect()
    print("App and asset parameters available after connect", app.app_configuration, app.assets, app.resources_map)

    # Custom Loop
    while True:
        random_value = round(random.random() * 10, 2)

        # Publish Data (Number)
        await app.publish(Number(resource=KRNAssetDataStream("asset1", "output-random-number"), payload=random_value))

        # Publish Data (String)
        await app.publish(
            String(resource=KRNAssetDataStream("asset1", "output-random-string"), payload=str(random_value))
        )

        # Publish Data (Boolean)
        await app.publish(
            Boolean(
                resource=KRNAssetDataStream("asset1", "output-random-boolean"), payload=random.choice([True, False])
            )
        )

        expiration_date = datetime.now() + timedelta(minutes=10)

        # Publish Control Change
        await app.publish(
            ControlChange(
                expiration_date=expiration_date,
                resource=KRNAssetDataStream("asset1", "output-cc-number"),
                payload=random_value,
            )
        )

        # Publish Recommendation
        await app.publish(
            Recommendation(
                type="generic",
                resource=KRNAsset("asset1"),
                expiration_date=timedelta(minutes=10),
                control_changes=[
                    ControlChange(
                        resource=KRNAssetDataStream("asset1", "output-cc-number"),
                        expiration_date=expiration_date,
                        retries=0,
                        timeout=300,
                        payload=random_value + 1,
                    )
                ],
            )
        )
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
