#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
blender_exec=`$SCRIPT_DIR/findblender.sh`
if [ -z "$blender_exec" ]
then
    (>&2 echo "Blender executable not found")
    exit 1
fi
echo "INVOCATION >> $blender_exec --background --python $@"
$blender_exec --background --python "$@"
