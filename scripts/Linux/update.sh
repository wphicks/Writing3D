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

function update_w3d {
    if type "git" > /dev/null
    then
        echo "Git found! Using Git to update..."
        git rev-parse HEAD > ../last_good.txt
        git fetch && git reset --hard origin/master || echo "Could not fetch update..."
    else
        echo "Git not found. Using Dulwich..."
        $SCRIPT_DIR/w3dpy.sh scripts/w3d_update.py || echo "Could not fetch update..."
    fi
}

cd Writing3D
$SCRIPT_DIR/w3dpy.sh scripts/blender_update.py || echo "Could not update Blender..."
$SCRIPT_DIR/w3dpy.sh scripts/dulwich_update.py || echo "Could not update Dulwich..."
update_w3d
