# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Allow running Python module as script: `python -m mmemoji` ([#94])

## [0.4.0] - 2022-03-27
### Changed
- Drop support for Python 3.6 which [has reached end-of-life](https://www.python.org/dev/peps/pep-0494/) ([#80])
- Drop `tablib` dependency. Support JSON and table outputs only ([#88])

### Fixed
- Set minimum dependencies versions ([#90])

## [0.3.1] - 2021-10-17
### Fixed
- Move `mypy-extensions` to main dependencies ([#23])

## [0.3.0] - 2021-10-17
### Added
- Add `download` command ([#8])
- Support for Python 3.8/3.9/3.10 ([#10])
- Enable Mypy static type checker ([#12])

### Changed
- Switch from `setuptools` to `poetry` ([#11])
- Switch from Travis CI to Github Actions ([#13])
- Rename `Emoji.emoji` property to `Emoji.metadata` ([#16])

### Fixed
- Remove accents in Emoji names instead of replacing characters by underscores ([#20])

### Removed
- Drop support for Python 3.5 which [has reached end-of-life](https://www.python.org/dev/peps/pep-0478/) ([#10])

## [0.2.0] - 2019-09-15
### Added
- Add `list` command ([#5])
- Add `search` command ([#5])
- documentation: Add deletion to examples ([#2])

### Changed
- Drop support for Python 3.4 which [has reached end-of-life](https://www.python.org/downloads/release/python-3410/) ([#6])
- Several bug fixes and enhancements to the test suite ([#1], [#3], [#4], [#6])

## [0.1.0] - 2019-01-08
### Added
- Initial release

[Unreleased]: https://github.com/maxbrunet/mmemoji/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/maxbrunet/mmemoji/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/maxbrunet/mmemoji/compare/v0.2.0...v0.3.1
[0.3.0]: https://github.com/maxbrunet/mmemoji/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/maxbrunet/mmemoji/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/maxbrunet/mmemoji/releases/tag/v0.1.0

[#94]: https://github.com/maxbrunet/mmemoji/issues/94
[#90]: https://github.com/maxbrunet/mmemoji/issues/90
[#88]: https://github.com/maxbrunet/mmemoji/issues/88
[#80]: https://github.com/maxbrunet/mmemoji/issues/80
[#23]: https://github.com/maxbrunet/mmemoji/issues/23
[#20]: https://github.com/maxbrunet/mmemoji/issues/20
[#16]: https://github.com/maxbrunet/mmemoji/issues/16
[#13]: https://github.com/maxbrunet/mmemoji/issues/13
[#12]: https://github.com/maxbrunet/mmemoji/issues/12
[#11]: https://github.com/maxbrunet/mmemoji/issues/11
[#10]: https://github.com/maxbrunet/mmemoji/issues/10
[#8]: https://github.com/maxbrunet/mmemoji/issues/8
[#6]: https://github.com/maxbrunet/mmemoji/issues/6
[#5]: https://github.com/maxbrunet/mmemoji/issues/5
[#4]: https://github.com/maxbrunet/mmemoji/issues/4
[#3]: https://github.com/maxbrunet/mmemoji/issues/3
[#2]: https://github.com/maxbrunet/mmemoji/issues/2
[#1]: https://github.com/maxbrunet/mmemoji/issues/1
