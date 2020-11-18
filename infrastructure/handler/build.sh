#!/bin/bash
set -e

rm -rf build
mkdir build
cp -R src/ build

pipenv lock -r > requirements.txt
pip install -r requirements.txt -t build --upgrade
