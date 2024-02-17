# ESI Releases

```{seealso}
Note that relevant info on USGS code distribution and repository metadata can be found at <https://www.usgs.gov/products/software/software-management/distribution-usgs-code>
```

## Description

This repository provides a CLI release tool for use in the repositories of the USGS Engineering Seismology and Impacts Gitlab group.

At present the CLI is a minimally functionally tool to increment major, minor, or patch version numbers in the code and update the project metadata in `code.json` accordingly.

For our purposes, this amounts to changing the `version` field in `code.json` followed by 3 URLs:

- 'downloardURL``
  - This URL is tied to a specific release on Gitlab based on a tag
- `disclaimerURL`  
- A `licenses` URL that exists under the `permissions` field

```{attention}
At the moment, this tool assumes that the version tag is of the form `v#.#.#`
```

## Installation

It can be installed directly from source by calling `pip` in the cloned repository base directory:

```python
pip install .
```

Developers or advanced users may which to include optional dependencies and install in editable mode:
```python
pip install -e .[dev,test,build]
```

The package is also availbe on PyPI and can be installed with:
```python
pip install esi-releases
```

## Usage

This CLI tool allows for three levels of version incrementation, depending on the scope of changes to a repostories code, and attempts to adhere to the conventions of Semantic Versioning

```python
<Major>.<Minor>.<Patch>
```

- Major version increments are used when new features that are backwards incompatible are introduced
- Minor version increments are used when new features that retain backwards compatibility are introduced
- Patch increments are used for bugfixes that do not introduce new features

The general behavior of this tool is the following:

- When a patch release is initiated, the patch number is simply incremented and adjusted across the metadata
- When a minor release is initiated, the minor number is incremented and the patch number is reset to zero
- When a major release is initiated, the major number is incremented, while the minor and patch numbers are reset to zero

### Commands

To initiate a release the following syntax is used:

```python
releases <major|minor|patch>
```

For example, for a package in a `patch` release at the a current version of `v1.0.0`:

```python
releases patch
```

will result in `v1.0.1`

Should the same package have a following 'minor' release, i.e.:

```python
releases minor
```

this will result in `v1.1.0`

Finally, if the package then undergoes a `major` release:

```python
releases major
```

the version will be incremented to `v2.0.0`

Help can be obtained in the CLI with the following:

```python
releases --help
```

## In Development

The intention of this CLI tool is to soon also support automate `CHANGELOG.md` updates based on commit messages in the repository, and to also prepare for a release by creating a new version entry. This is currently under development.
