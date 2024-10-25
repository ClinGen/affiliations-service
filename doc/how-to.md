# How-to Guides

Description from
[Divio documentation](https://docs.divio.com/documentation-system/how-to-guides/):

How-to guides take the reader through the steps required to solve a real-world
problem. They are directions to achieve a specific end. This page is
goal-oriented.

## Run Code Checks

How to run code checks before pushing a pull request.

Code should be:

1. automatically formatted using [Black](https://github.com/psf/black),
2. linted using [Pylint](https://github.com/pylint-dev/pylint),
3. type-checked using [mypy](https://mypy-lang.org/), and
4. tested using [Pytest](https://github.com/pytest-dev/pytest/).

To run these checks (see below for more information about Invoke):

```
inv check
```

### Utilizing Invoke

Invoke provides a high level API for running shell commands and
defining/organizing task functions from the `tasks.py` file. Invoke may be
executed as `invoke` (or `inv` for short).

You can see the list of our available invocations in our
[`tasks.py` file](../tasks.py) or by running `invoke --list` in your terminal.

More information can be found in the
[Invoke documentation here](https://www.pyinvoke.org/) and the
[getting started documentation here](https://docs.pyinvoke.org/en/stable/getting-started.html).

## Write Code That Can Be Submitted to the Main Branch

Expectations on how to write new code.

- Must pass the `check` script.
- New code must have automated tests.
- New code must have docstrings.
- If adding a new tool or something that other developers need to understand,
  there must be a tutorial for it.
- If a manual process is being added, there must be a how-to guide for it.
- If changing something significant (e.g. architecture) there should be a
  written explanation.
- If doing something complex or weird, there should be an explanation for it.

## Organize Imports and Constants

How to organize imports and constants in your file.

At the top of any given module there will probably be imports and constants. Our
preferred way of organizing them is as follows:

```
# Built-in libraries:
# [Built-in libraries go here.]

# Third-party dependencies:
# [Third-party dependencies installed via Pipenv go here.]

# In-house code:
# [In-house code imports go here.]

# Constants:
FOO = "foo"
BAR = 123
```

Each of the sections should be sorted alphabetically.

## Environment Variables

How to create environment variables. There's a `.env.template` file that is the
source of truth for environment variable keys.

- Create a copy of `.env.template` and name it `.env`
- Do not rename any of keys for the environment variables.
- Change the path for `AFFILS_DB_FILE` and placeholder values.

## Affiliation Service User Guides

TBD link to documentation for Affiliation Service users on how to do specific
tasks on the site.

## Contributing

How to contribute to the affiliations service.

Please see our [Contributing guidelines](./CONTRIBUTING.md) for more information
about contributing!

## Set up Postgres for local development

- Install Postgres version 16: `brew install postgresql@16`
- Start the database server: `brew services start postgresql@16`
- Enter the Postgres shell: `psql postgres`
- Create an Affiliations user:
  `CREATE ROLE affils_admin WITH LOGIN PASSWORD 'whateverYouWantForLocalDevelopment';`
- Add the user's name to the `.env` file
- Add the user's password to the `.env` file
- Give the new user permission to create databases:
  `ALTER ROLE affils_admin CREATEDB;`
- Quit out of the shell: `\q`
- Re-enter the shell as the `affils_admin` user: `psql postgres -U affils_admin`
- Check the list of roles to make sure the `affils_admin` user was given the
  correct permissions: `\du`
- Create the Affiliations database: `CREATE DATABASE affils;`
- Add the name of the database to the `.env` file
- Add the database engine (`postgresql`) to your `.env` file.
