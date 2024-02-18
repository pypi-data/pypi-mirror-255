#!/bin/bash

# List of documentation versions to keep.
# (should include all versions in switcher.json)
# Adding future versions will capture that version
# once it appears in the downloaded gh-pages branch.

versions=

# existing versions (to be kept)
versions+=" 1.0.0"
versions+=" 1.0.1"
versions+=" 1.0.3"
versions+=" 1.0.4"

# future versions (only expected release tags)
versions+=" 1.0.5"
versions+=" 1.0.6"
versions+=" 1.0.7"

export versions

# update file `docs/source/_static/switcher.json` before each new release
