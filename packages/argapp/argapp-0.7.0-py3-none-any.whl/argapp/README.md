# argapp - A Python package for CLI application development

# Overview

argapp is an OOP wrapper for [argparse](https://docs.python.org/3/library/argparse.html) and [argcomplete](https://pypi.org/project/argcomplete):
 * Allows writing CLI applications using OOP - encapsulates [argparse](https://docs.python.org/3/library/argparse.html) API.
 * Provides limited support for the shell completion via [argcomplete](https://pypi.org/project/argcomplete).

Full documentation is available at https://deohayer.github.io/argapp-ws.

## Features

 * Offers several classes for CLI parsing via OOP.
    * `Arg` represents optional and positional arguments, with the most essential use cases covered.
    * `App` represents a main command or a subcommand.
    * The fields are validated upon construction or setting, raising an `Exception` in case of any issues.
    * The parsing can be overridden by subclassing `Arg`.
 * Offers shell completion support if argcomplete is installed:
    * The required API calls are already in place. It is only required to install argcomplete and add the `PYTHON_ARGCOMPLETE_OK` comment to the script.
    * Specific completions are added automatically.

## Dependencies

 * Linux
 * Python 3
    * 3.6
    * 3.7
    * 3.8
    * 3.9
    * 3.10
    * 3.11

## Installation

 * The package can be installed globally by running:
   ```shell
   pip3 install argapp
   ```
 * The Git [repository](https://github.com/deohayer/argapp) can be used directly.
   The repository layout is designed with exactly this use case in mind.
 * For the argcomplete installation, please follow the official [documentation](https://pypi.org/project/argcomplete).

## Limitations

 * No abbreviated optional arguments.
 * No argument groups of any kind.
 * No partial parsing.
 * `argcomplete.autocomplete()` call is hidden and cannot be parametrized.
 * The completion has no test coverage.
