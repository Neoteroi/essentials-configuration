# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2021-08-11 :cactus:
- Forks a new project from
  [roconfiguration](https://github.com/Neoteroi/roconfiguration), with name
  `essentials-configuration`
- Implements a new code API that better supports extensions
- Makes `PyYAML` an optional dependency, necessary only if the user desires to
  use YAML files
- Applies `isort` and enforces `isort` and `black` checks in CI pipeline
