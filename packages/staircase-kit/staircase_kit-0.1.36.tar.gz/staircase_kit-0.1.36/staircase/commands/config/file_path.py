import click
import rich

from staircase.config import CONFIG_FILE_PATH
from staircase.lib.click import async_cmd


@click.command(name="file-path")
@async_cmd
async def command():
    rich.print(CONFIG_FILE_PATH)

