#!/bin/bash

PY_VER=$(python -c "import sys; print(sys.version.split(' ')[0])")

baseline() {
    echo -e "$1\n2.7" | sort -V | tail -n1
}

check() {
    [ "$1" = $(baseline $1) ]
}

if check $PY_VER; then
    python -m unittest discover
else
    unit2 discover
fi
