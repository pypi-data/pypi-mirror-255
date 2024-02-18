# poaster

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Minimal, libre bulletin board for posting announcements.

## Quickstart

Install package:

```console
pip install poaster
```

Run server:

```console
poaster
```

## Development

The easiest way to develop locally with `poaster` is to use [hatch](https://hatch.pypa.io/latest/). With `hatch`, you will have access to important helper scripts for running locally, linting, type-checks, testing, etc.

Run locally with:

```console
hatch run dev
```

Lint and check types with:

```console
hatch run types:check
```

Run test suite and report coverage with:

```console
hatch run cov
```

## License

`poaster` is distributed under the terms of the [AGPLv3](https://spdx.org/licenses/AGPL-3.0-or-later.html) license.
