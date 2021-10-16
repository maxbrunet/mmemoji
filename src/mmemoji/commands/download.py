import imghdr
import os
from typing import Any, List

import click
from requests import HTTPError

from mmemoji import Emoji
from mmemoji.decorators import parse_global_options


def check_destination(ctx: Any, param: click.Parameter, value: str) -> str:
    """Ensure destination is valid.

    For 1 emoji, the destination can be a file
    with an existing parent directory, or an existing directory,
    but if the destination is explicitly a directory,
    the full path must exits.

    For more than 1 emoji, the destination has to be an existing directory.

    Finally, the destination has to be writable.
    """
    count = len(ctx.params["emoji_names"])
    if count == 1 and value[-1] != os.path.sep and not os.path.isdir(value):
        directory = os.path.dirname(value) or os.getcwd()
    else:
        directory = value
    if not os.path.isdir(directory):
        raise click.ClickException("{}: Not a directory".format(directory))
    if (
        not os.access(directory, os.W_OK)
        or os.path.isfile(value)
        and not os.access(value, os.W_OK)
    ):
        raise click.ClickException("{}: Permission denied".format(directory))
    return value


@click.command(help="Download custom Emojis")
@click.argument("emoji_names", nargs=-1)
@click.argument("destination", callback=check_destination, type=click.Path())
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="do not prompt before overwriting (overrides -i option)",
)
@click.option(
    "-n",
    "--no-clobber",
    is_flag=True,
    help="do not overwrite an existing file (overrides -f and -i options)",
)
@click.option(
    "-i", "--interactive", is_flag=True, help="prompt before overwrite"
)
@parse_global_options
def cli(
    ctx: Any,
    emoji_names: List[str],
    destination: str,
    force: bool,
    no_clobber: bool,
    interactive: bool,
) -> None:
    try:
        for name in emoji_names:
            emoji = Emoji(ctx.mattermost, name)
            image = emoji.download()

            if not os.path.isdir(destination):
                filename = destination
            else:
                filename = os.path.join(
                    destination, "{}.{}".format(name, imghdr.what(None, image))
                )

            if os.path.exists(filename) and (
                not interactive
                and (no_clobber or not force)
                or interactive
                and not click.confirm(
                    'overwrite "{}"?'.format(filename), err=True
                )
            ):
                continue

            with open(filename, "wb") as f:
                f.write(image)
            click.echo(filename)
    except HTTPError as e:
        raise click.ClickException(e.args[0] if e.args != () else repr(e))
