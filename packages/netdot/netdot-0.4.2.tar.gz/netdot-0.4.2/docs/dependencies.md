
> ⚠ Reckless dependency management practices may result in [dependency hell](https://en.wikipedia.org/wiki/Dependency_hell).
> Anyone who depends on this package can find themselves in that hell if we mismanage our dependencies.
>
> ℹ Takeaway: Be mindful when handling the [production dependencies](#production-dependencies) -- take care to **follow the [guidelines provided below](#production-dependency-guidelines)**.

We use "pyproject.toml" to define all dependencies required to use this package -- i.e. the [production dependencies](#production-dependencies).
Meanwhile, the dependencies used by the development environment are managed in "hatch.toml" -- i.e. the [development dependencies](#development-dependencies).

## Production Dependencies

In "pyproject.toml" there is a `[project]` section. 
Within, there is the **minimum** list of packages required for installing the `netdot` package: 

    dependencies = [
      "configargparse >=1, <2",
      "humanize >=2",
      ... omitted for brevity...

### Production Dependency guidelines

This list should follow best practices, I.e.,

1. do **NOT** pin specific versions, and 
2. do **NOT** specify sub-dependencies.

## Development Dependencies

In "hatch.toml" there is the `[envs.dev]` section.
Within, similar to the "pyproject.toml" file, there is a list of packages required for installation: 

> ℹ Conceptually, these dependencies stack on top of the production dependencies -- e.g. when you [create your dev environment](development.md#getting-started) **all** the [production dependencies](#production-dependencies) will be installed before installing these dependencies.

    dependencies = [
      "pytest",
      "pytest-vcr",
      ... omitted for brevity...
