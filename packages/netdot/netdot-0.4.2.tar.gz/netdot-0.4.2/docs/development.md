This document discusses setting up local development for this project on your own personal Linux box. 

> We use [Python Hatch](https://hatch.pypa.io/latest/) for this project.

## Prerequisites

There are a pair of requirements for development:

* Python 3.12, and
* Hatch, which is discussed below.

### Hatch

We use Hatch to manage our development environment (and build process).

> What is Hatch? "Hatch is a modern, extensible Python project manager."

You can easily [install Hatch](https://hatch.pypa.io/latest/install/) using pip.

    pip install hatch

We advise running the following command once you've installed Hatch.
This will ensure virtual environments exist within the Hatch project's directory.

> This makes integrating with VSCode and other IDEs simpler.

    hatch config set dirs.env.virtual ./venv

## Getting Started

Once you have [installed Hatch](#hatch), we can jump right into our development environment using the following command.

    hatch shell

> ℹ At this point, running `pip freeze` should reveal that all dependencies are installed for you!

### Any Issues?

If there are issues during environment set up, it is generally best to start over from scratch.
This can be simply done by running `hatch env prune`.

> ℹ This will remove all Hatch-managed environments and restart fresh.
> 
> ℹ You will have to `exit` from any/all Hatch shells that you may have opened -- otherwise the prune will fail.


## Automated Testing

pytest is used to automatically test this project.
All tests are contained in the "tests" directory.

To run all the automated tests for this project, you can simply, "`run` the `tests` script provided by our `default` Hatch environment", I.e.: `hatch run tests`

    hatch run tests
    ===================== test session starts =====================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-1.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    ... omitted for brevity...

## Cleaning Up VCRpy Cassettes

We use the pytest-vcr plugin so that it is trivial to use VCRpy in our automated testing.
Over time, some cassettes might linger that don't have a test case anymore.

1. Get the name of all your cassettes (you'll need to save this output to a file, e.g. "cassettes.txt")
```bash
$ for f in *.yaml; do     printf '%s\n' "${f%.yaml}"; done
```
2. Then, get a report of all the test cases names (save the output to a different file)
```bash
$ pytest --co | grep Function | cut -d' ' -f4- | cut -d'>' -f1 | sort > pytest-all-tests.txt 
```
3. Ensure that both lists are sorted (Ex. using VS Code's "Sort Lines Ascending" command)
4. In VS Code, do "Select for Compare" on "cassettes.txt" vs "pytest-all-tests.txt"
5. Delete any cassette files that appear in "cassettes.txt" but not in "pytest-all-tests.txt"
> ℹ In other words, delete the cassette file corresponding to any ***redlines** that you see in "pytest-all-tests.txt"*

## Updating Hatch

It is wise to keep up to date with the latest hatch changes.

    python3.8 -m pip install --upgrade hatch

After updating Hatch, it is wise to ensure you are using the updated version of Hatch.
This is done using `hatch --version`.

    hatch --version
    Hatch, version 1.4.2

- Next, you will want to test the `hatch shell` feature.
- Finally, it is wise to ensure [Automated Tests pass](#automated-testing). ✅

> ⚠ TODO
> 
> When do we go about update the `hatchling` dependency declaration in pyproject.toml?
