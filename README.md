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
- codado.kleinish.tree: a decorator for klein @route methods that delegates
  into another class with a "subklein" of other routes

- urltool: A command-line tool that dumps klein routes from a project, when
  the project is using kleinish.tree

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
### [0.4.999] - 2017.12.12
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
  - fix a few build/install/test problems with setup.py/travis/tox
  - make unit tests stop relying on dict-ordering
  - urltool now outputs OpenAPI 3.0-spec docs by inspecting your app
### [0.4] - 2017.06.11
  - 0.4: Initial public usable release

[0.4.998]: https://github.com/corydodt/Codado/compare/release-0.4.0...release-0.4.998
[0.4]: https://github.com/corydodt/Codado/tree/release-0.4.0
