import json
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar
from urllib.parse import ParseResult, urlparse

import click
import requests.exceptions
from mattermostdriver import Driver as Mattermost
from mattermostdriver.exceptions import MethodNotAllowed
from mypy_extensions import KwArg, VarArg
from tabulate import tabulate

Decorator = TypeVar("Decorator", bound=Callable[..., Any])


def validate_url(ctx: Any, param: click.Parameter, value: str) -> ParseResult:
    """Ensure URL contains minimum information to be used"""
    url = urlparse(value)
    if not url.scheme or not url.hostname:
        raise click.BadParameter("Malformed URL: {}".format(value))
    return url


def compose(
    *decorators: Callable[[Decorator], Decorator]
) -> Callable[[Decorator], Decorator]:
    """Merge multiple decorators into a single one"""

    def decorate(func: Decorator) -> Decorator:
        for decorator in reversed(decorators):
            func = decorator(func)
        return func

    return decorate


global_options = compose(
    click.option(
        "-u",
        "--url",
        metavar="URL",
        envvar="MM_URL",
        callback=validate_url,
        required=True,
        help="Mattermost APIv4 URL (e.g http://localhost:8065/api/v4)"
        " (env: MM_URL)",
    ),
    click.option(
        "-t",
        "--token",
        metavar="TOKEN",
        envvar="MM_TOKEN",
        help="Personal Access Token (env: MM_TOKEN)",
    ),
    click.option(
        "-l",
        "--login-id",
        metavar="LOGIN_ID",
        envvar="MM_LOGIN_ID",
        help="login ID to use in conjunction with a password"
        " (env: MM_LOGIN_ID)",
    ),
    click.option(
        "-P",
        "--password",
        metavar="PASSWORD",
        envvar="MM_PASSWORD",
        help="password to use in conjunction with a login ID"
        " (env: MM_PASSWORD)",
    ),
    click.option(
        "-m",
        "--mfa-token",
        metavar="MFA_TOKEN",
        envvar="MM_MFA_TOKEN",
        help="optionally, Multi-Factor Authentication Token"
        " to use in conjunction with login ID/password"
        " (env: MM_MFA_TOKEN)",
    ),
    click.option(
        "-k",
        "--insecure",
        envvar="MM_INSECURE",
        is_flag=True,
        help="allow insecure server connections when using SSL"
        " (env: MM_INSECURE)",
    ),
    click.option(
        "--output",
        "-o",
        type=click.Choice(["json", "table"]),
        default="table",
        help="output format (default: table)",
    ),
)


# Workaround for the help option of subcommands not being eager enough
# The parent command is executed anyway
# https://github.com/pallets/click/issues/295
# https://github.com/pallets/click/issues/814
# This moves all global options to the subcommand which isn't that bad
# This way all options are visible when asking for help on a subcommand
def parse_global_options(
    func: Decorator,
) -> Callable[[VarArg(Any), KwArg(Any)], Any]:
    """Parse options used by every commands such as auth and output format"""

    @wraps(global_options(func))  # type: ignore
    @pass_context  # type: ignore
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx = args[0]
        ctx.output = kwargs.pop("output")
        with ctx.authenticate(
            kwargs.pop("url"),
            kwargs.pop("token"),
            kwargs.pop("login_id"),
            kwargs.pop("password"),
            kwargs.pop("mfa_token"),
            kwargs.pop("insecure"),
        ):
            return func(*args, **kwargs)

    return wrapper


class EmojiContext:
    """
    Custom Click Context class
    to store global settings and manage authentication
    """

    def __init__(self) -> None:
        self.output = "table"
        self.mattermost: Any = None

    @contextmanager
    def authenticate(
        self,
        url: ParseResult,
        token: str,
        login_id: str,
        password: str,
        mfa_token: str,
        insecure: bool,
    ) -> Any:
        """Authenticate against the Mattermost server"""

        if token and (login_id or password or mfa_token):
            click.echo(
                "Warning: Token specified along"
                " with Login-ID/Password/MFA-token."
                "Only Token will be used.",
                err=True,
            )

        settings = {
            "scheme": url.scheme,
            "url": url.hostname,
            "basepath": getattr(url, "path", ""),
            "verify": not insecure,
            "login_id": login_id,
            "password": password,
            "token": token,
            "mfa_token": mfa_token,
        }

        if url.port:
            settings["port"] = url.port
        elif url.scheme == "https":
            settings["port"] = 443
        else:
            settings["port"] = 80

        self.mattermost = Mattermost(settings)
        try:
            try:
                yield self.mattermost.login()
            finally:
                # Logout is unnecessary if token was used
                if token is None:
                    self.mattermost.logout()
        except (requests.exceptions.ConnectionError, MethodNotAllowed):
            raise click.ClickException(
                "Unable to reach Mattermost API at {}".format(
                    self.mattermost.client.url
                )
            )
        except requests.exceptions.HTTPError as e:
            raise click.ClickException(e.args[0] if e.args != () else repr(e))

    def print_dict(self, data: List[Dict[str, Any]]) -> None:
        """Print dataset generated by a command to the standard output"""
        count = len(data)
        if count:
            if self.output == "table":
                click.echo(tabulate(data, headers="keys"))
            else:
                click.echo(json.dumps(data, indent=2))

        click.echo(
            "\n({} emoji{})".format(count, "" if count == 1 else "s"),
            err=True,
        )


pass_context = click.make_pass_decorator(EmojiContext, ensure=True)
