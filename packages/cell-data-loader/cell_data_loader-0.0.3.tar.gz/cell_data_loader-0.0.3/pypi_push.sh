#!/bin/bash

rm -r dist
python3 -m build --sdist
twine upload dist/*
