#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
if [ -f ~/.w3d.json ]
then
    blender_exec=`grep -Po '(?<="Blender executable": ")[^"]*' ~/.w3d.json`
fi
if ! [ -z "$blender_exec" ]
then
    echo "$blender_exec"
    exit 0
fi

cd $SCRIPT_DIR

if [ -f ../../../blender/blender ]
then
    blender_exec="${PWD}/../../../blender/blender"
    echo "$blender_exec"
    exit 0
else
    if command -v blender >/dev/null 2>&1;
    then
        blender_exec="blender"
        echo "$blender_exec"
        exit 0
    else
        echo "Not found"
        exit 1
    fi
fi
