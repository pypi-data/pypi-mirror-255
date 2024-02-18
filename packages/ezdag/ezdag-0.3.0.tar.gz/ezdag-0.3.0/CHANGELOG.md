# Changelog

## [Unreleased]

## [0.3.0] - 2024-02-09

### Added

- Add string literals for use in Node arguments, inputs and outputs
- Allow extra meta-parameters to be defined at the node level (variables)
- Add log_dir as meta-parameter within submit description
- Generate log directories automatically upon DAG generation
- Allow the option prefix in Option to be configurable
- Add API access for DAG submission
- Simplify API for writing DAGs to disk using `DAG.write()`, writing both
  the DAG itself and also optionally the script with the list of commands

### Changed

- Change config argument in DAG to use a name instead, which was previously
  unused

### Removed

- Remove remap and suppress_with_remap options in Argument and Option,
  as this is now correctly handled via path types (absolute vs. relative)
  and whether file transfer is enabled

### Fixed

- Fix issue with output files being transferred in surpress edge case
- Fix general issues with file transfer when mixing absolute and relative
  paths
- Disable htcondor warnings when a valid condor config source isn't found
- Write commands in script file such that parent jobs are written first

## [0.2.0] - 2023-10-06

### Added

- Allow users to give submit description options using native Python
  types rather than understanding the correct formatting for each option
- Allow executables not found in PATH

### Changed

- Change requirements option to submit_description in Layer, keeping
  old option for backwards compatibility with a deprecation warning
- Allow customizable node name formatting from DAG
- Change default node name separator to avoid issues with common executable
  delimiters

### Removed

- Remove dynamic_memory option in Layer, as it had many implicit assumptions
  which are particularly brittle
- Remove periodic_release default in Layer

### Fixed

- Ensure node input/outputs are consistent for nodes upon Layer instantiation
- Avoid overwriting submit descriptors in Layer

## [0.1.0] - 2023-01-25

- Initial release.

[unreleased]: https://git.ligo.org/patrick.godwin/ezdag/-/compare/v0.3.0...main
[0.3.0]: https://git.ligo.org/patrick.godwin/ezdag/-/tags/v0.3.0
[0.2.0]: https://git.ligo.org/patrick.godwin/ezdag/-/tags/v0.2.0
[0.1.0]: https://git.ligo.org/patrick.godwin/ezdag/-/tags/v0.1.0
