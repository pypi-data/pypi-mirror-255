import asyncio
from typing import AsyncGenerator

from kelvin.application import KelvinApp, filters
from kelvin.message import Message


async def log_param(gen: AsyncGenerator[Message, None]):
    async for m in gen:
        print(f"Param ts={str(m.timestamp)} {str(m.resource)}({str(m.type)}): {m.payload}")


async def log_data(gen: AsyncGenerator[Message, None]):
    async for m in gen:
        print(f"Data ts={str(m.timestamp)} {str(m.resource)}({str(m.type)}): {m.payload}")


async def main():
    app = KelvinApp()

    param_stream = app.stream_filter(filters.is_parameter)
    data_stream = app.stream_filter(filters.is_data_message)

    tasks = {asyncio.create_task(log_param(param_stream)), asyncio.create_task(log_data(data_stream))}

    async with app:
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
