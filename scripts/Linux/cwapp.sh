#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
blender_exec=`$SCRIPT_DIR/findblender.sh`
if [ -z "$blender_exec" ]
then
    (>&2 echo "Blender executable not found")
    exit 1
fi
echo "INVOCATION >> $blender_exec --background --python $SCRIPT_DIR/../../samples/cwapp.py -- $1 $2"
$blender_exec --background --python "$SCRIPT_DIR/../../samples/cwapp.py" -- "$1" "$2"
