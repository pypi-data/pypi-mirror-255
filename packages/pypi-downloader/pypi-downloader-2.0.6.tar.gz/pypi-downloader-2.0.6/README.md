# pypi-downloader

## Description

This project can be used to mirror the pypi index using the new warehouse API.

This project consists of two scripts:

1. a multithreaded version of the main script, pypi-downloader-mt.py, as command: pypi-downloader
1. a helper script to get the current list of packages from the pypi index site currently located at: <https://pypi.org/>, as command: pypi-packages

## Config file

If a config file is specified as a command line parameter, the config file uses the YAML format.

The config file consists of four sections:

1. logging - Specifies a logging.dictConfig dictionary
1. threads - Number of threads to use
1. packages - List of packages to download, if no packages are specified, all packages are downloaded from the pypi index site
1. blacklist - List of packages to not download

Note: For logging, this module uses the root logger only.
Note: Values specified in the config file (threads and packages) can be overridden by values specified on the command line.

## Config file examples

### Default configuration

```yaml
logging:
  version: 1
  formatters:
    simple:
      format: '[%(levelname)s]: %(message)s'
  handlers:
    console1:
      class: logging.StreamHandler
      level: ERROR
      formatter: simple
      stream: ext://sys.stderr
    console2:
      class: logging.StreamHandler
      level: DEBUG
      formatter: simple
      stream: ext://sys.stdout
  root:
    level: INFO
    stream: ext://sys.stdout
    handlers: [console1, console2]
threads: 1
packages:
blacklist:
```

### Default configuration with packages and blacklist specified and non default thread count

```yaml
logging:
  version: 1
  formatters:
    simple:
      format: '[%(levelname)s]: %(message)s'
  handlers:
    console1:
      class: logging.StreamHandler
      level: ERROR
      formatter: simple
      stream: ext://sys.stderr
    console2:
      class: logging.StreamHandler
      level: DEBUG
      formatter: simple
      stream: ext://sys.stdout
  root:
    level: INFO
    stream: ext://sys.stdout
    handlers: [console1, console2]
threads: 5
packages:
  - tox
  - mypy
blacklist:
  - pyyaml
```
