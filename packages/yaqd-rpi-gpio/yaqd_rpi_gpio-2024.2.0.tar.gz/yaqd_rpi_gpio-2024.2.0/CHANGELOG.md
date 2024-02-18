# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [2024.2.0]

### Fixed
- digital-output still using self.position, must use state dictionary for modern yaq

## [2021.10.0]

### Changed
- regenerated avpr based on recent traits update

## [2021.3.0]

### Fixed
- added forgotten config options to is-daemon: enable, log_level, and log_to_file
- Update version of core for modified sensor behavior

## [2020.12.0]

### Changed
- regenerated avpr based on recent traits update

## [2020.08.0]

### Changed
- Now uses Avro-RPC [YEP-107](https://yeps.yaq.fyi/107/)
- Uses Flit for distribution

## [2020.06.1]

### Changed
- "value" is no longer written to state for gpio-digital-output
- gpio-digital-output now at version 0.2.0

### Added
- new daemon: gpio-digital-sensor

## [2020.06.0]

### Added
- initial release

[Unreleased]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2024.2.0...main
[2024.2.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2021.10.0...2024.2.0
[2021.10.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2021.3.0...2021.10.0
[2021.3.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2020.12.0...2021.3.0
[2020.12.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2020.08.0...2020.12.0
[2020.08.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2020.06.1...2020.08.0
[2020.06.1]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/compare/v2020.06.0...2020.06.1
[2020.06.0]: https://gitlab.com/yaq/yaqd-rpi-gpio/-/tags/v2020.06.0
