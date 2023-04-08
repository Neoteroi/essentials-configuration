# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2023-04-08 :egg:
- Renames the main namespace to `config`.
- Adds a method to obtain type checked configuration items (e.g. with `pydantic`
  or custom classes).
- Adds support to read secrets stored in the user folder, for development purpose.
- Adds a CLI to administer local secrets stored in the user folder.
- Adds a `FileConfigurationSource` base class.
- Migrates to `pyproject.toml`.
- Add support for `.env` files bound using `python-dotenv`.

## [1.0.0] - 2022-11-04 :snake:
- Upgrades pinned dependencies for Python 3.11
- Adds the alias "EnvVars" to reduce the verbosity of the class name "EnvironmentVariables"
- Adds support for TOML sources
- Replaces relative imports with absolute imports
- Workflow maintenance

## [0.0.2] - 2021-08-11 :cactus:
- Forks a new project from
  [roconfiguration](https://github.com/Neoteroi/roconfiguration), with name
  `essentials-configuration`
- Implements a new code API that better supports extensions
- Makes `PyYAML` an optional dependency, necessary only if the user desires to
  use YAML files
- Applies `isort` and enforces `isort` and `black` checks in CI pipeline
