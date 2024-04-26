# Changelog

## [0.?.0] - 2024-04-??

### Changed

- refactor package structure and exposed types (this includes the data-plumber base type `_DPType` being renamed to `DPType` and `Responses` being relocated into the new `settings`-module) (`6171d55`)
- changed `Object` such that the input `properties` are available publicly (`4bf9040`)
- `Object`-argument `additional_properties` now also accepts a boolean value (analogous to OpenAPI specification, defaults to `True` while `False` means only the given `properties` are accepted) (`f9991cb`)

### Added

- added `Any` as free-form field type (`139d126`)

### Fixed

- fixed problematic type hints in different places (`d76ae02`)

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
