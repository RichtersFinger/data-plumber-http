# Changelog

## [0.3.0] - 2024-04-16

### Added

- added `Null`-type (`1657715`)

### Fixed

- fixed potentially problematic `Property` where the `name`-property is an empty string (`409551d`)
- fixed issue where an `Object` with `model` causes crash when field is missing in input (`f7e30c2`)

## [0.2.0] - 2024-04-16

### Changed

- changed `Array` constructor argument `items` to allow `None` (accept any content from JSON) (`ee24833`)

### Added

- added `FileSystemObject`-type (`e1a648f`)
- added `Url`-type (`67eeb56`)


## [0.1.0] - 2024-04-15

- initial release
