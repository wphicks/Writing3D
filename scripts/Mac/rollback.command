#!/bin/bash
if [ ! -z "$BASH_SOURCE" ]
then
    SCRIPT_NAME="${BASH_SOURCE[0]}"
else
    SCRIPT_NAME="$0"
fi
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$SCRIPT_NAME" 2>/dev/null ||\
    greadlink -f "$SCRIPT_NAME" 2>/dev/null ||\
    echo "$SCRIPT_NAME")")" && pwd -P)"
cd "$SCRIPT_DIR/../../.."

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
