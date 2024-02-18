# di-logging

Product logging library to provide consistent logging across components.

Loggers can be obtained thusly:
```python
from di_logging import get_logger

logger = get_logger(__name__)
```
This code should be placed at the top level within a module and this logger used throughout the component.

If an application or system is being written the logging should be configured within the main entry point;
```python
from di_logging import configure_logging

if __name__ == "__main__":
    configure_logging()
    do_the_stuff()
```
This will setup the logging for the system.

## Release Process
&#9755; Includes a semantic release system, which generates a new release on GitHub, including a changelog.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The version is automatically changed accordingly to the commit message that results from merging the PR.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9755; `breaking-change/CAP-123` Something runs the pipeline and bumps major version: **1.0.0 → 2.0.0**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9755; `feature/CAP-123 Something` runs the pipeline and bumps minor version: **1.0.0 → 1.1.0**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9755; `fix/CAP-123 Something` runs the pipeline and bumps patch version: **1.0.0 → 1.0.1**

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9755; `CAP-123 Something` **just** runs the pipeline

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9888; If this flow is unclear to you, don't hesitate in contacting DevOps team &#9888;

## How to run locally

Create a `.env` file from the existent `.env.example` file. Make sure to update it accordingly with your environment variables.

### Using poetry
`poetry config virtualenvs.create true`
`poetry config virtualenvs.in-project true`
`poetry install`

### Using docker container

Execute `make start-dependencies` in order to start whichever dependencies your project might have. You should always have the base Python image.

Execute `make run` and your application should be running.

Execute `make stop-dependencies` when you no longer need to execute your project.

Execute `make sync-requirements` to rebuild the docker image.

#### How to know which `make` recipes are available

Run `make`

#### How to run tests

Run `make test`

#### How to run tests with coverage report

Run `make coverage`
