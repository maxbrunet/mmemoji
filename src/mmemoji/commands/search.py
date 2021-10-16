from typing import Any

import click
from requests import HTTPError

from mmemoji import Emoji
from mmemoji.decorators import parse_global_options


@click.command(help="Search custom Emojis (200 results maximum)")
@click.argument("term")
@click.option(
    "-p",
    "--prefix-only",
    is_flag=True,
    help="only search for names starting with the search term",
)
@parse_global_options
def cli(ctx: Any, term: str, prefix_only: bool) -> None:
    try:
        ctx.print_dict(Emoji.search(ctx.mattermost, term, prefix_only))
    except HTTPError as e:
        raise click.ClickException(e.args[0] if e.args != () else repr(e))
