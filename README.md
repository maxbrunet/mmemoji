[![PyPI][pypi badge]][pypi link]
[![Build Status][build badge]][build link]
[![Quality Gate][sonarcloud badge]][sonarcloud link]

# mmemoji

Custom Emoji manager command-line for [Mattermost][mattermost] 😎

Features:

* Create custom Emojis
* Delete custom Emojis
* List custom Emojis
* Search custom Emojis
* Export custom Emojis

## Installation


```shell
pip install mmemoji
mmemoji --help
```

_(Requires Python >=3.7)_

## Usage example

Let's take the [Party Parrot][COTPP] Emojis as an example.

* First, clone the Git repository or retrieve an archive of it:

```shell
git clone https://github.com/jmhobbs/cultofthepartyparrot.com.git
cd cultofthepartyparrot.com
```

* Then you'll need your Mattermost credentials. You can either pass them to `mmemoji` with the arguments `--url`/`--login-id`/`--password` or via environment variables, for example:

```shell
export MM_URL='http://127.0.0.1:8065/api/v4'
export MM_LOGIN_ID='user-1@sample.mattermost.com'
export MM_PASSWORD='user-1'
```

* Finally, run `mmemoji` to import all the parrots:

```shell
mmemoji create --no-clobber {parrots,guests}/hd/*.gif {parrots,guests}/*.gif
```

> _Notes_:
>
> * Here we rely on [shell globbing][glob] to select all emojis from the directories.
> * Specifying the `hd` directories first with `--no-clobber` ensures these emojis are created first and not overwritten by their lower quality counterpart.

* If you ever want to remove them all, simply run the following:

```shell
mmemoji delete --force {parrots,guests}/hd/*.gif {parrots,guests}/*.gif
```

> _Notes_:
>
> * The emoji names are extracted from the filenames the same way they have been during creation.
> * `--force` is used to ignore the absent low quality duplicates.

## Development

* You can clone this repository and install the project with [Poetry][poetry]:

```shell
poetry install
```

* You'll find a script to create a local [Docker][docker] test instance under `tests/`:

```shell
./tests/scripts/setup-mattermost.sh
```

* You can run the test suite with:

```shell
pytest
```

* And last thing, you can install the [pre-commit][pre-commit] hooks to help with the formatting of your code.

```shell
pre-commit install
```

[pypi badge]: https://img.shields.io/pypi/v/mmemoji.svg
[pypi link]: https://pypi.python.org/pypi/mmemoji
[build badge]: https://github.com/maxbrunet/mmemoji/actions/workflows/build.yml/badge.svg
[build link]: https://github.com/maxbrunet/mmemoji/actions/workflows/build.yml
[sonarcloud badge]: https://sonarcloud.io/api/project_badges/measure?project=maxbrunet_mmemoji&metric=alert_status
[sonarcloud link]: https://sonarcloud.io/dashboard?id=maxbrunet_mmemoji
[mattermost]: https://www.mattermost.org
[COTPP]: https://cultofthepartyparrot.com
[glob]: https://en.wikipedia.org/wiki/Glob_(programming)
[poetry]: https://python-poetry.org/docs/
[docker]: https://www.docker.com
[pre-commit]: https://pre-commit.com
