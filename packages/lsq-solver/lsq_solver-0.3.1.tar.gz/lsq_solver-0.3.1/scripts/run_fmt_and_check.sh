#!/bin/sh
hatch run autopep8 src tests
hatch run ruff src tests