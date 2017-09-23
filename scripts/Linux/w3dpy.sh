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
blender_exec="$("${SCRIPT_DIR}/findblender.sh")"
blender_site_script="${SCRIPT_DIR}/../amend_blender_site.py"

if [ -z "$blender_exec" ]
then
    (>&2 echo "Blender executable not found")
    exit 1
fi

echo "INVOCATION >> $blender_exec --background --python $@"

"$blender_exec" --background --python "$blender_site_script"
"$blender_exec" --background --python "$@"
