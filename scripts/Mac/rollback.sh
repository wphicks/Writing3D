#!/bin/bash
if [ ! -z "$BASH_SOURCE" ]
then
    SCRIPT_NAME="${BASH_SOURCE[0]}"
else
    SCRIPT_NAME="$0"
fi
if command -v readlink > /dev/null 2>&1
then
    SCRIPT_DIR="$(dirname "$(readlink -f "$SCRIPT_NAME")")"
else
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_NAME")" && pwd -P)"
fi
cd "$SCRIPT_DIR"

if [[ -f "last_good.txt" ]]
then
    cd Writing3D
    git checkout `cat ../last_good.txt`
elif [[ -f "last_good.zip" ]]
then
    rm -rf Writing3D
    unzip last_good.zip
else
    echo "No previous good configuration found. Could not rollback."
fi
