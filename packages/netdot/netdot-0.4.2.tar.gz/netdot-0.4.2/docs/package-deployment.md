# Package Deployment

This project has CICD established via our [Jenkins server](https://is-nts-jenkins.uoregon.edu).

## Deployment Checklist

Before delivering a new version of this package, these are key steps.

- [ ] Update declared dependencies, if needed.
- [ ] Ensure all existing automated tests pass.
    - [ ] **BONUS POINTS**: Ensure code coverage of any new code.
- [ ] Ensure any production functionality has not regressed (best effort).
- [ ] Run `hatch run gendocs` 
    - [ ] Ensure that the updated "docs/generated-*-docs.md" files look good.
- [ ] Update the version, following [Semantic Versioning](http://semver.org).
    * E.g. `hatch version patch|minor|major`
- [ ] Update Release Notes, to include the new version.
- [ ] Update the User Guide with any relevant changes.
- [ ] Complete the [Deployment Workflow (below)](#deployment-workflow).
- [ ] Once the package is in PyPI, ensure you can download and install the new package version successfully.

## Deployment Workflow

Our Continuous Integration and Delivery (CICD) are triggered by Pull Requests.
The workflow to trigger a new deployment is the very simple pull request workflow (annotated with CICD steps):

1. **`git push`** your new branch to the Source Control Management (SCM) server.
2. Log in to the SCM server and **create a pull request**.
    * CI runs at this point (running all automated tests).
3. Once Jenkins has completed its CI run, **merge** the pull request
    * CD runs at this point (deploying to the appropriate Python Package Index)

## Release Candidate Workflow

To make a release candidate, add `[release-candidate-N]` in your last git commit before opening a pull request.

    git commit --allow-empty -m '[release-candidate-24] Release candidate'
    git push

Now, simply proceed with the normal [Deployment Workflow](#deployment-workflow) to see your release candidate published to PyPI!

> ℹ Tip: This can actually be done anytime after the pull request is opened, but before merging the pull request.