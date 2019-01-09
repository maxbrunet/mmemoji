import click
from requests import HTTPError

from mmemoji import Emoji
from mmemoji.decorators import parse_global_options


@click.command(help="Create custom Emojis")
@click.argument("images", type=click.File("rb", lazy=True), nargs=-1)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="""
if the emoji exists, remove it and proceed \
(this option is ignored when the -i or -n option is also used)
""",
)
@click.option(
    "-n",
    "--no-clobber",
    is_flag=True,
    help="do not overwrite an existing file (overrides -i option)",
)
@click.option(
    "-i", "--interactive", is_flag=True, help="prompt before overwrite"
)
@parse_global_options
def cli(ctx, images, force, no_clobber, interactive):
    emojis = []

    try:
        with click.progressbar(images, show_pos=True) as pb_images:
            for image in pb_images:
                emoji = Emoji(ctx.mattermost, image.name)

                if emoji.emoji and not no_clobber and interactive:
                    force = click.confirm(
                        'overwrite "{}"?'.format(emoji.name), err=True
                    )
                    if not force:
                        continue

                with image as img:
                    if emoji.create(img, force, no_clobber):
                        emojis.append(emoji.emoji)
    except HTTPError as e:
        raise click.ClickException(e.args if e.args != () else repr(e))
    finally:
        ctx.print_dict(emojis)
