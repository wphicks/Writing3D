#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
blender_exec=`$SCRIPT_DIR/findblender.sh`
blender_site_script="$SCRIPT_DIR/../amend_blender_site.py"

if [ -z "$blender_exec" ]
then
    (>&2 echo "Blender executable not found")
    exit 1
fi

echo "INVOCATION >> $blender_exec --background --python $@"

echo $blender_site_script
$blender_exec --background --python "$blender_site_script"
$blender_exec --background --python "$@"
