from pathlib import Path

import toml  # with python3.11 this can be replaced by tomllib from stdlib
import typer
from rich import print as rprint

from .validators import validate_config
from .. import __version__


def config_callback(ctx: typer.Context, configfile_path: Path):
    if ctx.resilient_parsing:
        return

    if configfile_path.exists():
        with configfile_path.open('rt') as configfile:
            config = toml.loads(configfile.read())
    else:
        config = {}
    validate_config(config)

    defaults = dict(config.pop('defaults', {}))
    ctx.default_map = ctx.default_map or {}  # preserve existing defaults
    ctx.default_map.update(defaults)

    ctx.ensure_object(dict)
    ctx.obj['config'] = config


def version_callback(flag: bool):
    if flag:
        rprint(f'[bold][green]pve-cli Version:[/green] [blue]{__version__}[blue][/bold]')
        raise typer.Exit()
