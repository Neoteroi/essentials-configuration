<!-- generated file, to update use: python examples-summary.py -->

# Examples

## example-01.py

This example illustrates how data can be fetched from a source (YAMLFile) and read
into an instance of a specific type (FooSettings), validated using pydantic.

This example has a single source for the sake of simplicity, but in normal situations
several layers would be used (e.g. settings file, env specific settings file, env
variables, etc.).


## example-02.py

This example shows how to load app settings from a TOML file, and from
environment variables, filtered by "APP_" prefix.


## example-03.py

This example shows how to load app settings from a JSON file, and from
environment variables, filtered by "APP_" prefix and obtained from a .env file
(this is optional!), and how values can be overridden.


## example-04.py

This example illustrates a way to override settings from a common file, using an
environment specific settings file.


## example-05.py

This example shows how nested values can be overridden using strings.


## example-06.py

This example shows how to override nested properties in arrays using
environment variables.


## example-07.py

This example shows how to override nested properties using environment
variables.
