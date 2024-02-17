# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs


Report bugs at https://git.illumina.com/CGR/DUX4r_caller/issues.

If you are reporting a bug, make it as reproducible as possible:

* Reproduce it inside a public docker image (e.g. python:3.10).
* Provide your operating system name and version, version of Python used.
* Provide details on how you setup your local environment.
* Provide detailed steps to reproduce the bug, possibly providing the simplest
  complete example (e.g. produce a small bam file that would reproduce the
  error and make it available).


## Get Started!

Ready to contribute? Here's how to set up `pelops` for local development.

* Fork the `dux4r_caller` repo on GitHub.
* Clone your fork locally:

   ```shell
   git clone git@github.com:your_name_here/dux4r_caller.git
   ```

* Install dependencies to run all the tests, and make sure `master` runs all
  the tests successfully before modifying the source code:

   ```shell
   pip install -r requirements-dev.txt
   make devinstall
   # unit tests only
   make unittest
   # also check typing annotation is correct
   make tests
   ```

   If there are any issue, sort them out before proceeding

* You are now ready to create a branch for local development:

   ```shell
   git checkout -b name-of-your-bugfix-or-feature
   ```
   Now you can make your changes locally.

*  When you're done making changes, check that your changes pass
   [Black](https://pypi.org/project/black/) and run the test again

   ```shell
   black --check .
   make tests
   ```

* Commit your changes and push your branch to GitHub::
   ```shell
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin -u name-of-your-bugfix-or-feature
   ```

* Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

* The pull request should include tests.
* If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
* The pull request should work for Python 3.7, 3.9 and 3.11. Check
   https://git.illumina.com/CGR/DUX4r_caller/actions
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests::
```shell
pytest --verbose --exitfirst tests/test_entities.py
```
