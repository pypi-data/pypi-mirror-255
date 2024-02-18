#!/bin/bash
#
################################
# build.sh
################################
# Purpose:
#       This script compiles a platform-specific pip wheel for bulgogi-py.
# Usage:
#       Run `./build.sh` on the target platform.
#       The necessary build deps will be fetched, compiled and later linked into a pip wheel.
################################

source gitinit.sh

python3 setup.py build_ext

python3 -m build
