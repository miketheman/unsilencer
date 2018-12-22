# unsilencer

A tool to interact with [MailGun](https://www.mailgun.com/)'s
[API](https://documentation.mailgun.com/en/latest/api_reference.html) to handle
[suppressions](https://help.mailgun.com/hc/en-us/articles/360012287493-What-are-Mailgun-Suppressions-).

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Takes an email address as an input, checks to see if the address appears on these lists:

-   unsubscribes
-   complaints
-   bounces

If the address appears, it will then be removed from each list.

## Requirements

-   [Python](https://www.python.org/) 3.7
-   [Pipenv](https://github.com/pypa/pipenv)

## Installation

    git clone https://github.com/WarbyParker/unsilencer.git
    cd unsilencer/
    pipenv install
    # Alternately, if you want to develop the code:
    pipenv install --dev

## Configuration

Set environment variables:

-   `MAILGUN_API_KEY` - see [docs](https://documentation.mailgun.com/en/latest/api-intro.html#authentication). Looks like: `key-<hash>`
-   `MAILGUN_DOMAIN_NAME` - the domain owning the suppression lists being checked

## Usage

Once installed and configured, execute via `pipenv`:

    pipenv run python unsilencer.py foo@bar.com

Alternately, enter Pipenv's environment and execute:

    pipenv shell
    python unsilencer.py foo@bar.com

## Development

Uses [pytest](https://pytest.org/) test suite, with a bunch of plugins to help with code quality.

Execute tests:

    pipenv run pytest

Read a blog from [PyBites](https://pybit.es/pytest-coding-100-tests.html) if you're unfamiliar with pytest!

## Authors

-   [Mike Fiedler](https://github.com/miketheman)
