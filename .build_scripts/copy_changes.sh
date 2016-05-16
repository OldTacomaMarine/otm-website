#!/usr/bin/env sh

mkdir "build"
mkdir "build_no_cache"

cp www/* build
mv build/index.html build_no_cache

