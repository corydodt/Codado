# Codado [![Build Status](https://travis-ci.org/corydodt/Codado.svg?branch=master)](https://travis-ci.org/corydodt/Codado)
A library of utilities for systems application development

## Tools included:

- codado.enum: a simple key-(optional value) enumerator builder
- codado.eachMethod: a class decorator that applies a method decorator to every
  method matching a pattern
- codado.fromdir: returns a function that gives paths from a particular location
- codado.remoji: returns a random, value-neutral emoji from a curated list
- codado.utcnowTZ: utcnow, but there's actually a timezone on it
- codado.parseDate: sensible datestring parser
- codado.tx.Main: a Twisted Usage helper that creates a useful main() function
- codado.dockerish: a docker event listener that integrates with the Twisted
  event loop and can automatically call handlers for events
  into another class with a "subklein" of other routes
- codado.hotedit: open a local editor with a string, edit it as a temp file and get the edited string back

## Running Tests

```
$ tox
```

## Build/upload

Make sure to:

- Update version in setup.py
- Update the Change Log below
- **Commit the changes to the above files**
- ```
  python3 setup.py sdist bdist_wheel && python2 setup.py bdist_wheel
  ```
- Add and push a tag for the new release
- ```
  $ twine upload dist/*
  ```

## Change Log

### [0.8.0] - 2020.12.18
#### Fixed:
  - Fix hotedit invocation in Python 3 (check_output returns bytes) (#21)
  - This change officially breaks backwards compatibility with Python 2

### [0.7.6] - 2020.02.26
#### Changed:
  - The version of mock is no longer strictly specified, allowing higher versions to be used while this package is installed
  - Fix find_packages usage in setup.py

### [0.7.4] - 2019.11.26
#### Added:
  - hotedit.hotedit() for opening your favorite local editor and getting the results back as a string

### [0.7.2] - 2019.07.23
#### Fixed:
  - stop overspecifying python-dateutil to allow dependents to install more easily

### [0.7.0] - 2019.07.03
#### Removed:
  - codado.kleinish (deprecated since 0.5) (#9)
  - codado.py.doc (deprecated since 0.5) (#9)

### [0.6.1] - 2018.09.12
#### Added:
  - Codado fully supports Python 3.6+

#### Changed:
  - Twisted is now a fullblown dependency of Codado, no longer optional

  - In Python 3, changes to sorting behavior mean that you can no longer include non-string keys
    safely in your JSON AMP messages; all keys should be strings. (This was good practice anyway,
    Python was silently converting them to strings.) Removed a test for this behavior.

### [0.5.2] - 2018.04.21
#### Changed:
  - Permit recent versions of pytz to be installed

### [0.5.1] - 2017.12.29
#### Added:
  - For backward compatibility, restore `codado.kleinish.tree` and `.openapi` (which are still deprecated)

### [0.5.0] - 2017.12.29
#### Added:
  - fix `install_requires` missing `mock` to help pip installation
  - textHTML() and applicationJSON() helpers to mark klein routes as having
    responses
  - queryParameter() to mark klein routes as taking parameters
  - parseDate() and utcnowTZ()
  - remoji()
  - Flag `--reverse` (`-v`) for urltool filters
  - LottaPatches() test tool
#### Changed:
  - All of `codado.kleinish` is DEPRECATED. This corresponds to the release of [Crosscap] 0.1.0, which takes over this functionality. Kleinish will be removed from codado by the 0.6.0 release.
  - `codado.py.doc` is DEPRECATED. This is also now found in Crosscap, and will be removed by 0.6.0.
  - fix a few build/install/test problems with setup.py/travis/tox
  - make unit tests stop relying on dict-ordering
  - urltool now outputs OpenAPI 3.0-spec docs by inspecting your app

### [0.4] - 2017.06.11
  - 0.4: Initial public usable release

[Crosscap]: https://github.com/corydodt/Crosscap
[0.8.0]: https://github.com/corydodt/Codado/compare/release-0.7.6...release-0.8.0
[0.7.6]: https://github.com/corydodt/Codado/compare/release-0.7.4...release-0.7.6
[0.7.4]: https://github.com/corydodt/Codado/compare/release-0.7.2...release-0.7.4
[0.7.2]: https://github.com/corydodt/Codado/compare/release-0.7.0...release-0.7.2
[0.7.0]: https://github.com/corydodt/Codado/compare/release-0.6.1...release-0.7.0
[0.6.1]: https://github.com/corydodt/Codado/compare/release-0.5.2...release-0.6.1
[0.5.2]: https://github.com/corydodt/Codado/compare/release-0.5.1...release-0.5.2
[0.5.1]: https://github.com/corydodt/Codado/compare/release-0.5.0...release-0.5.1
[0.5.0]: https://github.com/corydodt/Codado/compare/release-0.4.0...release-0.5.0
[0.4]: https://github.com/corydodt/Codado/tree/release-0.4.0
