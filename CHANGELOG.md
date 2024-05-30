# Changelog

## [1.0.0] - 2024-05-30

### Changed

- replaced `Number`-related argument `range` by individual arguments for lower and upper bounds (`97d076b`)
- improved response-messages for invalid `FileSystemObject`s (`0511c8f`)
- refactored `Responses` into a singleton (`ef69fc6`)
- refactor package structure and exposed types (this includes the data-plumber base type `_DPType` being renamed to `DPType` and `Responses` being relocated into the new `settings`-module) (`6171d55`)
- changed `Object` such that the input `properties` are available publicly (`4bf9040`)
- `Object`-argument `additional_properties` now also accepts a boolean value (analogous to OpenAPI specification, defaults to `True` while `False` means only the given `properties` are accepted) (`f9991cb`)

### Added

- added `py.typed`-marker (`686fc72`)
- added `Uri`-type (`4602db2`)
- added `OneOf` and `AllOf` for conditional structures (`47d1430`)
- added `Any` as free-form field type (`139d126`)

### Removed

- remove old argument `fill_with_none` from `Property` (`bc8b91f`)

### Fixed

- fixed `model`-argument for `Object` (`f9991cb`)

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
