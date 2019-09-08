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
def cli(ctx, term, prefix_only):
    try:
        ctx.print_dict(Emoji.search(ctx.mattermost, term, prefix_only))
    except HTTPError as e:
        raise click.ClickException(e.args if e.args != () else repr(e))
