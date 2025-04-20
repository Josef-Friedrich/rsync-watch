# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

<small>[Compare with latest](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.8.0...HEAD)</small>

## [v0.8.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.8.0) - 2025-04-20

<small>[Compare with v0.7.2](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.7.2...v0.8.0)</small>

### Added

- Add option to ignore specific exceptions (none-zero exit codes)


## [v0.7.2](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.7.2) - 2024-02-15

<small>[Compare with v0.7.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.7.1...v0.7.2)</small>

### Changed

- Switch testing framework from nose2 to pytest

### Fixed

- Fix some typing issues ([b25e590](https://github.com/Josef-Friedrich/rsync-watch/commit/b25e590b60c238c3bec20ab6ac29e2cf3f2c427a) by Josef Friedrich).

## [v0.7.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.7.1) - 2023-04-11

<small>[Compare with v0.7.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.7.0...v0.7.1)</small>

### Fixed

- Fix parsing of numbers containing dots

### Added

- Add test ([eed504a](https://github.com/Josef-Friedrich/rsync-watch/commit/eed504a3c17f8d7bc44960ee38b510887e782745) by Josef Friedrich).

## [v0.7.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.7.0) - 2022-08-22

<small>[Compare with v0.6.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.6.0...v0.7.0)</small>

### Added

- Add some type hints ([f5e831d](https://github.com/Josef-Friedrich/rsync-watch/commit/f5e831d92e6e99d2ff7579c7f0c55da4139a2e65) by Josef Friedrich).

## [v0.6.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.6.0) - 2022-08-22

<small>[Compare with v0.5.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.5.0...v0.6.0)</small>

### Added

- Add tooling support for black and isort ([69531d8](https://github.com/Josef-Friedrich/rsync-watch/commit/69531d81b15f1160c7e4759b3c500ff50328f8b9) by Josef Friedrich).
- Add templates for the badges ([98bec98](https://github.com/Josef-Friedrich/rsync-watch/commit/98bec9844c9ba1dde958c21660eb23d945b29d76) by Josef Friedrich).

### Fixed

- Fix tests ([60872c0](https://github.com/Josef-Friedrich/rsync-watch/commit/60872c009c2ce79d59d661b1a2f9e97d6274b50a) by Josef Friedrich).
- Fix duplicate keys in pyproject.toml ([c6f0e98](https://github.com/Josef-Friedrich/rsync-watch/commit/c6f0e98ba30d695d6fd140882f8cc45c4f8c970a) by Josef Friedrich).

## [v0.5.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.5.0) - 2022-07-19

<small>[Compare with v0.4.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.4.1...v0.5.0)</small>

### Added

- Add README_template.rst ([11ac208](https://github.com/Josef-Friedrich/rsync-watch/commit/11ac208b11abc466831d4b4f36526bf2bcaeef35) by Josef Friedrich).
- Add license classifiers in pyproject.toml ([a772030](https://github.com/Josef-Friedrich/rsync-watch/commit/a77203082cdb2d7dfd26d7ec1660d18d6e8fdfb9) by Josef Friedrich).
- Add pyproject.toml ([8e4947b](https://github.com/Josef-Friedrich/rsync-watch/commit/8e4947b99d2a4307496a51e4882692058fa5c4b7) by Josef Friedrich).
- Add type hints ([bfd5c07](https://github.com/Josef-Friedrich/rsync-watch/commit/bfd5c07c8859decb3754eb14bc169bc2ce97c75d) by Josef Friedrich).
- Add some types ([7b6cbc4](https://github.com/Josef-Friedrich/rsync-watch/commit/7b6cbc4685688e933251d98f51af9d1775f1531a) by Josef Friedrich).
- Add some typs ([f3129b2](https://github.com/Josef-Friedrich/rsync-watch/commit/f3129b26d0940e37a11918718bc57ff7f985c0bf) by Josef Friedrich).
- Add Makefile for upload task ([1dbe8db](https://github.com/Josef-Friedrich/rsync-watch/commit/1dbe8dbd31925dfb0041c0065e9f671b43425ab9) by Josef Friedrich).

### Fixed

- Fix duplicate deps key ([32d2a63](https://github.com/Josef-Friedrich/rsync-watch/commit/32d2a6367d0a757e350192ec400efc78c41e9391) by Josef Friedrich).
- Fix zsh:1: no matches found: --usermap=*:smb ([7777d70](https://github.com/Josef-Friedrich/rsync-watch/commit/7777d70d69b9798bd8e7f59df233272c867c78f0) by Josef Friedrich).

### Removed

- Remove the u prefix of same strings ([981737f](https://github.com/Josef-Friedrich/rsync-watch/commit/981737fba5423ff91b40034fce6332ce5fb3a2cc) by Josef Friedrich).
- Remove further files that belonged to the versioneer ([81889aa](https://github.com/Josef-Friedrich/rsync-watch/commit/81889aaa8ca8bc3900ab4e7d1725548e4be7ae26) by Josef Friedrich).
- Remove versioneer ([89889b2](https://github.com/Josef-Friedrich/rsync-watch/commit/89889b2ae02f181ca65e31083769abe40a51b506) by Josef Friedrich).

## [v0.4.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.4.1) - 2019-07-08

<small>[Compare with v0.4.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.4.0...v0.4.1)</small>

### Removed

- Remove --beep option. Use --beep-activated from jflib command_watcher ([be66eab](https://github.com/Josef-Friedrich/rsync-watch/commit/be66eab4f525c4912a2a235ddd44b71013acf112) by Josef Friedrich).

## [v0.4.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.4.0) - 2019-07-08

<small>[Compare with v0.3.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.3.1...v0.4.0)</small>

## [v0.3.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.3.1) - 2019-07-08

<small>[Compare with v0.3.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.3.0...v0.3.1)</small>

## [v0.3.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.3.0) - 2019-07-08

<small>[Compare with v0.2.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.2.1...v0.3.0)</small>

## [v0.2.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.2.1) - 2019-05-11

<small>[Compare with v0.2.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.2.0...v0.2.1)</small>

### Fixed

- Fix match object is not subscriptable on Python 3.5 ([a3ebcb5](https://github.com/Josef-Friedrich/rsync-watch/commit/a3ebcb5013b85f7b3489ae9ccf0f95cc6157a0f3) by Josef Friedrich).

## [v0.2.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.2.0) - 2019-05-11

<small>[Compare with v0.1.3](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.1.3...v0.2.0)</small>

### Added

- Add support for pyton 3.5 ([e677af5](https://github.com/Josef-Friedrich/rsync-watch/commit/e677af5b9b029a4d0fee909f94caf151f72db22e) by Josef Friedrich).

## [v0.1.3](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.1.3) - 2019-05-06

<small>[Compare with v0.1.2](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.1.2...v0.1.3)</small>

## [v0.1.2](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.1.2) - 2019-05-05

<small>[Compare with v0.1.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.1.1...v0.1.2)</small>

### Fixed

- Fix config_reader reader order ([db6ae8c](https://github.com/Josef-Friedrich/rsync-watch/commit/db6ae8c5d4ae21dc872cfdc645194ecac42e47b0) by Josef Friedrich).

## [v0.1.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.1.1) - 2019-05-05

<small>[Compare with v0.1.0](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.1.0...v0.1.1)</small>

### Fixed

- Fix config file issue ([0d42007](https://github.com/Josef-Friedrich/rsync-watch/commit/0d420072ddcd6091bc16d142600488dc65e1e85f) by Josef Friedrich).

## [v0.1.0](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.1.0) - 2019-05-05

<small>[Compare with v0.0.13](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.13...v0.1.0)</small>

### Fixed

- Fix all tests ([8c6d094](https://github.com/Josef-Friedrich/rsync-watch/commit/8c6d094c88638c62d331863319ad4e250116dd6a) by Josef Friedrich).
- Fix some tests ([d84ae7e](https://github.com/Josef-Friedrich/rsync-watch/commit/d84ae7edccad411c7e4ea316f716a84e227a1856) by Josef Friedrich).

## [v0.0.13](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.13) - 2019-04-17

<small>[Compare with v0.0.12](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.12...v0.0.13)</small>

### Added

- Add more log messages ([cd1f981](https://github.com/Josef-Friedrich/rsync-watch/commit/cd1f981f80a9a276f49618609ccae6e66083bb03) by Josef Friedrich).
- Add color ([6a68950](https://github.com/Josef-Friedrich/rsync-watch/commit/6a689500870670b60849ca9a73b37ea02235a59d) by Josef Friedrich).
- Add custom handler ([a0ab6e3](https://github.com/Josef-Friedrich/rsync-watch/commit/a0ab6e3b3013c4724e77d2528a819390d7284b9a) by Josef Friedrich).

### Fixed

- Fix all texts ([a1a7d0d](https://github.com/Josef-Friedrich/rsync-watch/commit/a1a7d0d1cb35f78682129fb738ef0f19c9c114b6) by Josef Friedrich).
- Fix some tests ([6dfd525](https://github.com/Josef-Friedrich/rsync-watch/commit/6dfd52552a32d9dfc510856ddb3dfa97cb9ee7e4) by Josef Friedrich).
- Fix docs for readthedocs ([350eefa](https://github.com/Josef-Friedrich/rsync-watch/commit/350eefa69350ca0443f1ce5b82375554190c04e3) by Josef Friedrich).
- Fix some errors ([1e5a6d4](https://github.com/Josef-Friedrich/rsync-watch/commit/1e5a6d4d5fbea85355eeb6c859ec864e970f4c9a) by Josef Friedrich).

## [v0.0.12](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.12) - 2019-04-10

<small>[Compare with v0.0.11](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.11...v0.0.12)</small>

## [v0.0.11](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.11) - 2019-04-09

<small>[Compare with v0.0.10](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.10...v0.0.11)</small>

## [v0.0.10](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.10) - 2019-04-09

<small>[Compare with v0.0.9](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.9...v0.0.10)</small>

### Added

- Add the readthedocs badge ([a1d9387](https://github.com/Josef-Friedrich/rsync-watch/commit/a1d9387e7216dee8c69f2c0066c1fa57fd6e15eb) by Josef Friedrich).
- Add more docs ([217321e](https://github.com/Josef-Friedrich/rsync-watch/commit/217321e06d0771fef814a55493c746905ddea4b6) by Josef Friedrich).
- Add tox support ([ac05a00](https://github.com/Josef-Friedrich/rsync-watch/commit/ac05a00573ad1738525a5ea6dcac6c6c328dc027) by Josef Friedrich).

### Fixed

- Fix sphinx build on read the docs ([6a24810](https://github.com/Josef-Friedrich/rsync-watch/commit/6a24810ec122a8657e30f4a49aca67670cf017fa) by Josef Friedrich).

## [v0.0.9](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.9) - 2019-03-24

<small>[Compare with v0.0.8](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.8...v0.0.9)</small>

### Fixed

- Fix TypeError: expected str, bytes or os.PathLike object, not int: Integer in args list ([eea9035](https://github.com/Josef-Friedrich/rsync-watch/commit/eea9035628d3328a5f7a83d41f559ea07bb9d00f) by Josef Friedrich).

## [v0.0.8](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.8) - 2019-03-24

<small>[Compare with v0.0.7](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.7...v0.0.8)</small>

### Fixed

- Fix stats parsing: missing deleted files ([89d0a6c](https://github.com/Josef-Friedrich/rsync-watch/commit/89d0a6c48faf7b1c35877036b4f08070aab4a5dc) by Josef Friedrich).

## [v0.0.7](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.7) - 2019-03-24

<small>[Compare with v0.0.6](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.6...v0.0.7)</small>

## [v0.0.6](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.6) - 2019-03-20

<small>[Compare with v0.0.5](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.5...v0.0.6)</small>

## [v0.0.5](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.5) - 2019-03-19

<small>[Compare with v0.0.4](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.4...v0.0.5)</small>

### Added

- Add new options ([1f00648](https://github.com/Josef-Friedrich/rsync-watch/commit/1f00648f413a34034c00c3e4fcf29dc470070388) by Josef Friedrich).

## [v0.0.4](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.4) - 2019-03-19

<small>[Compare with v0.0.3](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.3...v0.0.4)</small>

### Added

- Add more output ([ac757d7](https://github.com/Josef-Friedrich/rsync-watch/commit/ac757d7fb6f88670ad9fd1c16ec528c1c82c112b) by Josef Friedrich).

## [v0.0.3](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.3) - 2019-03-18

<small>[Compare with v0.0.2](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.2...v0.0.3)</small>

## [v0.0.2](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.2) - 2019-03-18

<small>[Compare with v0.0.1](https://github.com/Josef-Friedrich/rsync-watch/compare/v0.0.1...v0.0.2)</small>

### Added

- Add send_nsca source code ([70e007c](https://github.com/Josef-Friedrich/rsync-watch/commit/70e007cd81e8b1124f00d2006cf308e73893cc9d) by Josef Friedrich).

## [v0.0.1](https://github.com/Josef-Friedrich/rsync-watch/releases/tag/v0.0.1) - 2019-03-18

<small>[Compare with first commit](https://github.com/Josef-Friedrich/rsync-watch/compare/274563dad7fafbbae9e21cca7b9d763f7db4403a...v0.0.1)</small>

### Added

- Add requirements ([5e48841](https://github.com/Josef-Friedrich/rsync-watch/commit/5e4884175e7a1a998d62463d0dcfe63acd00343b) by Josef Friedrich).
- Add travis shield ([cc945c0](https://github.com/Josef-Friedrich/rsync-watch/commit/cc945c02aeb890404cd318228c9b8f4d6569e2db) by Josef Friedrich).
- Add script skeleton ([6167798](https://github.com/Josef-Friedrich/rsync-watch/commit/61677985edc52d6c8a98be2045b9c966503c5567) by Josef Friedrich).

### Fixed

- Fix travis yml extension ([9e92e33](https://github.com/Josef-Friedrich/rsync-watch/commit/9e92e33c1f329d8b5d66ed47bb404ecef13a400d) by Josef Friedrich).
