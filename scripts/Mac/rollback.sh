#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $SCRIPT_DIR

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
