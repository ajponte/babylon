[![babylon-server](https://github.com/ajponte/babylon/actions/workflows/python-app.yml/badge.svg)](https://github.com/ajponte/babylon/actions/workflows/python-app.yml)

# babylon
Personal finance aggregation &amp; analysis

## Package Management
### Poetry
This project uses `poetry` for package management.

### Tox Automation
This project includes a `tox.ini` file to automate tasks such as
* invoking pytest
* linting
* formatting
* type-checking
* distribution building.

A fresh `tox` build can be invoked via `tox -r`, which whill invoke each task.
See https://github.com/tox-dev/tox for more info.

### Distribution
A local distribution of the package can be created either through
```shell
 poetry build
```
or
```shell
 tos -e dist
```
Since the build is dependent on `poetry`, the commands are equivalent.

### Unit Tests
This project uses `pytest`. You can invoke tests in a poetry environment, via
```shell
 poetry run pytest tests
```

### Formatting
This project uses `black` to enforce PEP-8 formatting rules.
You can format any file with
```shell
 poetry run black <target>
```
where `<target>` is the directory or file to run the tool on.

With `tox`, you can also check formatting any time with
```shell
 tox -e format
```
Note that since tox is intended to be invoked as part of a CI
pipeline, we will never rewrite files.

### Type Checking
This project (somewhat) enforces static typing through `mypy`.

## Local Development
Services are mocked in `docker-compose.yml`.
A new stack can be brought up with

``` shell
    docker-compose up -d
```

Note that there's a `healthcheck` step in setting up the postgres container.

The stack can be completely brought down with
```shell
    # Adding the `-v` flag will remove attached volumes.
    docker-compose down -v
```
