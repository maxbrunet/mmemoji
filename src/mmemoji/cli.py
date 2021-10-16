import logging
import os
from typing import Any, List, cast

import click

from mmemoji import __summary__, __version__

logging.getLogger("mattermostdriver.websocket").disabled = True


class EmojiCLI(click.MultiCommand):
    """Custom Click Command class to dynamically discover subcommands"""

    def list_commands(self, ctx: Any) -> List[str]:
        rv = []
        cmd_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "commands")
        )
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename == "__init__.py":
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx: Any, name: str) -> click.Command:
        try:
            module = __import__(
                "mmemoji.commands." + name, None, None, ["cli"]
            )
            return cast(click.Command, module.cli)
        except ModuleNotFoundError:
            raise click.ClickException(
                'Unknown command "{}" for "{}"\n'
                "Run '{} --help' for usage.".format(
                    name, ctx.info_name, ctx.info_name
                )
            )


@click.command(name="mmemoji", cls=EmojiCLI, help=__summary__)
@click.version_option(version=__version__, message="%(prog)s %(version)s")
def cli() -> None:
    """CLI entry-point"""
    pass
