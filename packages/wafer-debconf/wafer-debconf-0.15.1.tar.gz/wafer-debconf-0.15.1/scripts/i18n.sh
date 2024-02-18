#!/bin/sh

set -eu

apps="debconf minidebconf"

for app in $apps; do
  echo $app
  (
    cd $app
    mkdir -p locale
    ../manage.py makemessages --all --keep-pot
    find locale -name \*.pot -or -name \*.po | xargs --no-run-if-empty sed -i -e "s/^#: /#: $app\//"
  )
done
