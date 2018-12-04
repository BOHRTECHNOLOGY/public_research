# Software development guidelines

Author: Konrad Jałowiecki

## Purpose and scope of this note

This note is a follow-up after discussion we had during CVRP project retrospection.
The aim is to formalize guidelines for:

- structuring Python projects in a way that guarantees convenient usage and development.
- writing Python code to ensure coherent style among participating programmers.
- using git version control system

Most of the recommendations presented here are backed up either by some PEP, official
Python documentation or another reliable source - when this is the case we provide the source
to the information. As with most things, this note may be somewhat biased by the author's preferences and previous experience in Python programming and software development.

## Python project structure

What we recommend for project structure is a widely accepted layout of `setuptools`
compatible package. We mostly follow Kenneth Reitz's recommendations available in his
[essay](https://www.kennethreitz.org/essays/repository-structure-and-python). The example
project presented in the essay has been stripped down to necessary components.

### Directory layout

Below we may see a layout of minimal project structure named `sample` highlighting possible components of a project
(some of them may be optional, see below)

```text
sample
- docs
- README.rst
- requirements.txt
- sample
- setup.py
- tests
```

The components of the project are (sorted in descending order of importance):

- code

  The code is placed inside a Python package (i.e. a directory with `__init__.py` file in it) with the same name as the project itself. According to [PEP8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names) It is adviced that this package, as well as other packages, does not contain an underscore - however, this is only a convention as there are no technical reasons why underscores should be avoided.

- tests

  Tests should be placed in a directory that is sibling to the code. It is possible to include tests
  inside the code directory but separating them is a practice followed by many open source projects and has a benefit of not polluting site packages when the package is installed in production mode.
  Recommended framework for preparing and running tests is [`pytest`](https://docs.pytest.org/en/latest/).
  
- setup file

  The setup file `setup.py` contains meta information about the project, requirements and versioning information. Providing `setup.py` file allows one to install a package using `pip`. This aspect is crucial for the ease of use of the package, whether in production or benchmarking process, as it can be installed in production and development mode. Recommended package for creating setup script is `setuptools`, see tool recommendations in [Python packaging guide](https://packaging.python.org/guides/tool-recommendations/).

- documentation

  Documentation, if any, is usually placed in docs directory sibling to tests and code.

- additional files

  Additional files like license, README, Manifest should be placed in the top level directory. Such placement is mostly required by `setuptools`.

- requirements file

  This is purely optional. Using `setup.py` file is usually sufficient. However, requirements file might be handy if you want to separate development requirements from production ones.

### Why use setuptools or bother with making package installable?

Python enforces neither specific directory structure nor compatibility with `setuptools`. It is therefore important to understand why making package installable is important from multiple perspectives.

- Making package installable makes it easy for deployment. Deploying `setuptools` package boils down to installing it with `pip` using a single command. Note that the package can also include installable scripts/command line tools that will be globally available after package installation.

- As a consequence installable package is easier to use during benchmarks and experiments. Instead of adding code as a subtree (like we do now) we can install package inside a virtual environment and just import it in benchmark code.

- Package can be installed in [editable](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) (development) mode (using `-e` switch with `pip`). When in development mode, package files are not copied inside site packages directory and instead symbolic links are created. You can, therefore, edit the code and have changes immediately visible in your Python environment. Therefore, changes introduced during the experiment can be easily propagated to the main repository, again without using git subtree.

To install a package in editable mode run the below command in the package directory

```bash
pip install -e .
```

## Style guide

For most things conforming to [PEP8](https://www.python.org/dev/peps/pep-0008/) is recommended. Here we only highlight several guidelines. Please note that every style choice should be considered on a case-by-case basis, the rules below should not be treated as written in stone.

- Try keeping your lines short. PEP8 is slightly conservative and recommends limiting line length to 80 characters. It seems that setting 100 characters as the maximum limit is reasonable, this is also a default setting in pylint (see [source](https://github.com/PyCQA/pylint/blob/master/pylintrc)).

- Try reducing nesting level. As indicated in [Python Zen](https://www.python.org/dev/peps/pep-0020/), "Flat is better than nested". A highly nested code is more difficult to test and read. If applicable, write helper functions/methods or use `itertools` functions for complicated iterations.

- Use descriptive names for variables, if it doesn't make them extremely long. Possible exceptions can include well-known constants/attributes (e.g. if you write `Point` class there is nothing wrong in naming its components `x`, `y`, `z`).

- It's more important that code is easy to understand for someone new to the project than that's concise.

The following is not strictly connected to style but rather to general software engineering (applicable not only in Python).

- Write classes that have preferably a single responsibility. This rule is called Single Responsibility Principle and is a part of [SOLID](https://en.wikipedia.org/wiki/SOLID) design principles.

## Recommended guidelines for using git

This section covers basic guidelines for using git VCS.

- Commit often. Try to keep your commits atomic, adding single coherent change at a time.
- Use separate branch for new features. If you are working on larger projects, structure your branches in a hierarchical manner (e.g. `myproject/feature1`, `myproject/feature2` etc.)
- Use imperative mode when writing commit messages. So instead of "Adds function foo" consider using "Add function foo". Sticking to imperative mode always saves some characters and is consistent with git messages after merge or revert.
- Avoid committing incomplete work. Your reason to commit should not be that you need your working tree clean - in such cases, it is better to use stashes.
