import click
from requests import HTTPError

from mmemoji import Emoji
from mmemoji.decorators import EmojiContext, parse_global_options


@click.command(help="List custom Emojis")
@parse_global_options
def cli(ctx: EmojiContext) -> None:
    try:
        ctx.print_dict(Emoji.list(ctx.mattermost))
    except HTTPError as e:
        raise click.ClickException(e.args[0] if e.args != () else repr(e))
