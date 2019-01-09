import click
from requests import HTTPError

from mmemoji import Emoji
from mmemoji.decorators import parse_global_options


@click.command(help="Delete custom Emojis")
@click.argument("emoji_names", nargs=-1)
@click.option("-f", "--force", is_flag=True, help="ignore nonexistent files")
@click.option(
    "-i", "--interactive", is_flag=True, help="prompt before every removal"
)
@parse_global_options
def cli(ctx, emoji_names, force, interactive):
    emojis = []
    try:
        with click.progressbar(emoji_names, show_pos=True) as pb_names:
            for name in pb_names:
                emoji = Emoji(ctx.mattermost, name)

                if (
                    interactive
                    and emoji.emoji
                    and not click.confirm(
                        'delete "{}"?'.format(emoji.name), err=True
                    )
                ):
                    continue

                if emoji.delete(force):
                    emojis.append(emoji.emoji)
    except HTTPError as e:
        raise click.ClickException(e.args if e.args != () else repr(e))
    finally:
        ctx.print_dict(emojis)
