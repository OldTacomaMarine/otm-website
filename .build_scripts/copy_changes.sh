#!/usr/bin/env sh

mkdir "build"

#git diff-tree -r --no-commit-id --name-only --diff-filter=ACMRT HEAD www/ | xargs -I '{}' cp '{}' build
cp -r www/* build
