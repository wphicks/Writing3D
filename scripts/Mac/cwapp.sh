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
if [ -z "$blender_exec" ]
then
    (>&2 echo "Blender executable not found")
    exit 1
fi
echo "INVOCATION >> $blender_exec --background --python ${SCRIPT_DIR}/../../samples/cwapp.py -- ${1} ${2}"
"$blender_exec" --background --python "${SCRIPT_DIR}/../../samples/cwapp.py" -- "${1}" "${2}"
