import asyncio
from asyncio import Queue
from typing import AsyncGenerator

from kelvin.application import KelvinApp, filters
from kelvin.message import KRNAssetDataStream, Message, Number


async def on_connect():
    print("Hello, it's connected")


async def on_data(msg: Message):
    print(f"Hello, got a message: {msg.resource} = {msg.payload}")


async def on_disconnect():
    print("Hello, it's disconnected")


async def on_parameter(msg: Message):
    print("Hello, it's parameter")
    print(msg)


async def handle_queue(queue: Queue):
    while True:
        msg = await queue.get()
        print("Received metric1: ", msg)


async def handle_stream(stream: AsyncGenerator[Message, None]):
    async for msg in stream:
        print("Received metric2: ", msg)


async def main():
    app = KelvinApp()
    app.on_connect = on_connect
    app.on_asset_input = on_data
    app.on_disconnect = on_disconnect
    app.on_app_parameter = on_parameter
    app.on_asset_parameter = on_parameter

    queue1 = app.filter(filters.resource_equals(KRNAssetDataStream("asset1", "metric1")))
    asyncio.create_task(handle_queue(queue1))

    stream2 = app.stream_filter(filters.resource_equals(KRNAssetDataStream("asset1", "metric2")))
    asyncio.create_task(handle_stream(stream2))

    await app.connect()

    while True:
        m = Number(resource=KRNAssetDataStream("asset-1", "x-both"), payload=123.5)
        print("Sending message: ", m)
        await app.publish(m)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
