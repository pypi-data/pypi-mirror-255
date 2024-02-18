# neoval-py-utils

Python Utilities

# Development

All development must take place on a feature branch and a pull request is required; a user is not allowed to commit directly to `main`. The automated workflow in this repo (using `python-semantic-release`) requires the use of [angular style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) commit messages to update the package version and `CHANGELOG`. All commits must be formatted in this way before a user is able to merge a PR; a user who may want to develop without using this format for all commits can simply squash non-angular commit messages prior to merge. A PR may only be merged by the `rebase and merge` method. This is to ensure that only angular style commits end up on `main`.

Upon merge to `main`, the `deploy` workflow will facilitate the following:

- bump the version in `pyproject.toml`
- update the `CHANGELOG` using all commits added
- tag and release, if required
- publish to PyPi
