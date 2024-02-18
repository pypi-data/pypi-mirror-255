# DPN Python Utils

A collection of python utils used by the DPN.

Target minimum python version: `3.12.x`

## High-level Design Notes

To be broadly compatible with running in synchronous or asynchronous mode.

The principles behind the modules are to:

-   Be dependable and provide least surprise
-   Fail safe and raise informative exceptions
-   Optimize code for readability and maintainability
-   Design for backwards compatibility

Major versions of dpn_pyutils releases track major Python versions in general
availability

## Modules

| Module Name  | Module Description                                      |
| ------------ | :------------------------------------------------------ |
| `cli`        | Methods relating to command line input and output       |
| `common`     | Methods relating to logging and shared system services  |
| `crypto`     | Methods relating to cryptography and encoding           |
| `exceptions` | Exception classes for all modules                       |
| `file`       | Methods relating to file and path operations            |
| `http`       | Methods relating to general HTTP/REST                   |
| `money`      | Methods relating to money, transactions, and formatting |
| `time`       | Methods relating to time management                     |

## Getting Started

The fastest way to get start is with a [pyenv](https://realpython.com/intro-to-pyenv/).

With pyenv installed on the system, check the latest version of the target python version.

```bash
pyenv update && pyenv install -l | grep 3.12
```

### Install

Install with pip using:

```bash
pip install dpn_pyutils
```

### Install manually

Install the target python version into pyenv and set up the virtualenv

```bash
pyenv install 3.12.1
pyenv virtualenv 3.12.1 dpn_pyutils
pyenv activate dpn_pyutils
pip install --upgrade pip poetry
poetry install
```

### Upgrade versions

Upgrading is done by uninstalling the package and installing the upgraded version

```bash
pip install --upgrade dpn_pyutils
```

## Building

Building dpn_pyutils can be done with python 3 and poetry

```bash
tox run-parallel
poetry build
```

The distribution-ready files will be in the `dist/` directory.

## Packaging and Distribution

Packaging after changes need the following to be executed:

### Update the version number

Bump the version number

-   The MAJOR and MINOR versions should **always** match the minimum Python versions
-   The PATCH version should be an incremental counter of library versions

```bash
poetry check --lock
git commit -am"Updated requirements, pyproject and bumping version number for release"
```

### Distribute

```bash
poetry build
poetry publish
```
