import logging
import os

import click

from mmemoji.version import DESCRIPTION, VERSION

logging.getLogger("mattermostdriver.websocket").disabled = True


class EmojiCLI(click.MultiCommand):
    """Custom Click Command class to dynamically discover subcommands"""

    def list_commands(self, ctx):
        rv = []
        cmd_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "commands")
        )
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and not filename == "__init__.py":
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        module = __import__("mmemoji.commands." + name, None, None, ["cli"])
        return module.cli


@click.command(name="mmemoji", cls=EmojiCLI, help=DESCRIPTION)
@click.version_option(version=VERSION, message="%(prog)s %(version)s")
def cli():
    """CLI entry-point"""
    pass
