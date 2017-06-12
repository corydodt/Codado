# Codado [![Build Status](https://travis-ci.org/corydodt/Codado.svg?branch=master)](https://travis-ci.org/corydodt/Codado)
A library of utilities for systems application development

## Running Tests

```
$ tox
```

## Tools included:

- codado.enum: a simple key-(optional value) enumerator builder
- codado.eachMethod: a class decorator that applies a method decorator to every
  method matching a pattern
- codado.fromdir: returns a function that gives paths from a particular location
- codado.tx.Main: a Twisted Usage helper that creates a useful main() function
- codado.dockerish: a docker event listener that integrates with the Twisted
  event loop and can automatically call handlers for events
- codado.kleinish.tree: a decorator for klein @route methods that delegates
  into another class with a "subklein" of other routes

- urltool: A command-line tool that dumps klein routes from a project, when
  the project is using kleinish.tree

