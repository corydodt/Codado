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

## Running Tests

```
$ tox
```

##  Build/upload

Make sure to:

- Update codado/_version.py
- Update the Change Log below

```
$ python setup.py sdist bdist_wheel
$ twine upload dist/*
```

## Change Log
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
[0.5.2]: https://github.com/corydodt/Codado/compare/release-0.5.1...release-0.5.2
[0.5.1]: https://github.com/corydodt/Codado/compare/release-0.5.0...release-0.5.1
[0.5.0]: https://github.com/corydodt/Codado/compare/release-0.4.0...release-0.5.0
[0.4]: https://github.com/corydodt/Codado/tree/release-0.4.0
