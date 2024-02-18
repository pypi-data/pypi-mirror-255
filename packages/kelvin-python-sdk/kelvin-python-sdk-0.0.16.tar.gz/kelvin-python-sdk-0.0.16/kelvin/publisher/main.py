from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable, Optional

import click
import yaml

from .config import AppConfig
from .publisher import CSVPublisher, PublishServer, Simulator


def coro(f: Callable) -> Any:
    """
    Decorator to allow async click commands.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
def kelvin_publisher() -> None:
    pass


@kelvin_publisher.command()
@coro
@click.option(
    "--config",
    required=True,
    default="app.yaml",
    type=click.STRING,
    show_default=True,
    help="Path to the app config file",
)
@click.option("--period", default=5, type=click.FLOAT, show_default=True, help="Publish period in seconds")
@click.option("--min", default=0, type=click.FLOAT, show_default=True, help="Minimum value to publish")
@click.option("--max", default=100, type=click.FLOAT, show_default=True, help="Maximum value to publish")
@click.option(
    "--random/--counter", "rand", default=True, show_default=True, help="Publish random values or incremental"
)
@click.option("--asset-count", type=click.INT, help="Number of test assets from 'test-asset-1' to 'test-asset-N'")
@click.option(
    "--asset-parameter",
    type=click.STRING,
    help="Override asset parameters eg --asset-parameters kelvin_closed_loop=true  (Can be set multiple times)",
    multiple=True,
)
async def simulator(
    config: str,
    period: float,
    min: float,
    max: float,
    rand: bool,
    asset_count: Optional[int],
    asset_parameter: list[str],
) -> None:
    """Generates random data to application's inputs"""
    try:
        with open(config) as f:
            config_yaml = yaml.safe_load(f)
            app_config = AppConfig.parse_obj(config_yaml)
    except FileNotFoundError:
        print(
            f"Error: Unable to locate the application configuration file. config={config}\n"
            "Please make sure you are in the application directory or specify the path using the --config option."
        )
        return

    assets_extra = []
    # if no assets set on app yaml set asset_count default to 1
    if len(app_config.app.kelvin.assets) == 0 and asset_count is None:
        asset_count = 1

    if asset_count is not None:
        assets_extra = [f"test-asset-{i+1}" for i in range(asset_count)]

    gen = Simulator(app_config, period=period, rand_min=min, rand_max=max, random=rand, assets_extra=assets_extra)
    pub = PublishServer(app_config, generator=gen)

    if len(assets_extra) > 0:
        pub.add_extra_assets(assets_extra=assets_extra)

    for p in asset_parameter:
        param, value = p.split("=", 1)
        pub.update_param(asset="", param=param, value=value)

    await pub.start_server()


@kelvin_publisher.command()
@coro
@click.option(
    "--config",
    required=True,
    default="app.yaml",
    type=click.STRING,
    show_default=True,
    help="Path to the app config file",
)
@click.option("--csv", required=True, type=click.Path(exists=True), help="Path to the csv file to publish")
@click.option(
    "--publish-rate",
    required=False,
    type=click.FLOAT,
    show_default=True,
    help="Publish period in seconds. Publish csv rows at this rate instead of the rate determined between timestamps. \
[default: 1 -> if the csv has no timestamp column]",
)
@click.option(
    "--offset-timestamps",
    is_flag=True,
    default=False,
    show_default=True,
    help="offsets the (first) csv timestamp to current time (now)",
)
@click.option("--asset-count", type=click.INT, help="Number of test assets from 'test-asset-1' to 'test-asset-N'")
@click.option(
    "--asset-parameter",
    type=click.STRING,
    help="Override asset parameters eg --asset-parameters kelvin_closed_loop=true  (Can be set multiple times)",
    multiple=True,
)
async def csv(
    config: str,
    csv: str,
    publish_rate: Optional[float],
    offset_timestamps: bool,
    asset_count: Optional[int],
    asset_parameter: list[str],
) -> None:
    """Publishes data from a csv to the application.
    The publishing rate is determined by the difference between timestamps in the csv rows.
    """
    try:
        with open(config) as f:
            config_yaml = yaml.safe_load(f)
            app_config = AppConfig.parse_obj(config_yaml)
    except FileNotFoundError:
        print(
            f"Error: Unable to locate the application configuration file. config={config}\n"
            "Please make sure you are in the application directory or specify the path using the --config option."
        )
        return

    assets_extra = []
    # if no assets set on app yaml set asset_count default to 1
    if len(app_config.app.kelvin.assets) == 0 and asset_count is None:
        asset_count = 1

    if asset_count is not None:
        assets_extra = [f"test-asset-{i+1}" for i in range(asset_count)]

    gen = CSVPublisher(csv, publish_rate, offset_timestamps)
    pub = PublishServer(app_config, generator=gen)

    if len(assets_extra) > 0:
        pub.add_extra_assets(assets_extra=assets_extra)

    for p in asset_parameter:
        param, value = p.split("=", 1)
        pub.update_param(asset="", param=param, value=value)

    await pub.start_server()


def main() -> None:
    try:
        asyncio.run(kelvin_publisher())
    except KeyboardInterrupt:
        print("Shutdown.")


if __name__ == "__main__":
    main()
