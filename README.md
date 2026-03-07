[![babylon-server](https://github.com/ajponte/babylon/actions/workflows/python-app.yml/badge.svg)](https://github.com/ajponte/babylon/actions/workflows/babylon-server.yml)

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
 tox -e dist
```
Since the build is dependent on `poetry`, the commands are equivalent.

### Artifact Deployment
This project supports building and deploying `babylon` as a Zip module artifact.
The build process is managed by `tox`, which is the source of truth for creating the artifact.

To build the artifact locally:
```shell
tox -e build-artifact
```
This will produce a `babylon.zip` file in the root directory containing the built distribution.

#### Automated Deployment
The `artifact_upload.py` script is used to build and upload the artifact to GitHub. It is integrated into the CD workflow in `.github/workflows/deploy-artifact.yml`.

To run the upload script manually:
```shell
python artifact_upload.py --repo <owner/repo> --tag <tag_name> --pat-token <your_token>
```
The script will:
1. Run `tox -e build-artifact` to generate the zip file.
2. Create or update a GitHub Release with the specified tag.
3. Upload `babylon.zip` as a release asset.

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
### Update DB Connection
Because docker-compose uses DHCP, container IP addresses could change. A quick way to fetch the IP address
of the postgres container is to use the following command:
```shell
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres
```
