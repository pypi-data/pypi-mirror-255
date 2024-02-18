#!/bin/sh

set -eu

for dir in "$1"/dist/*; do
  theme=$(basename "${dir}")
  mkdir -p ${theme}/static
  touch ${theme}/__init__.py
  cp "${dir}/_variables.scss" ${theme}/static/
  cp "${dir}/_bootswatch.scss" ${theme}/static/
  ln -sfT ../LICENSE.bootswatch "${theme}"/LICENSE
done

cp "${1}"/LICENSE LICENSE.bootswatch
