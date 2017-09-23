#!/bin/bash
set -eu -o pipefail
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
REPO_DIR="$SCRIPT_DIR/.."
ROOT_DIR="$REPO_DIR/.."
BUILD_DIR="$ROOT_DIR/W3DBuilds"

function sync {
    cd "$BUILD_DIR"
    sftp -b "$SCRIPT_DIR/Linux/dev/deploy-unstable.sftp" w3dhost
}

function create_platform_specifics {
    cd "$SCRIPT_DIR"
    for dir in `ls -d */`
    do
        platform=${dir%?}
        cd "$ROOT_DIR/W3DZip-$platform/Writing3D"
        git fetch --tags
        git reset --hard origin/develop
        for script in `ls scripts/$dir`
        do
            script_loc="scripts/$platform/$script"
            if ! [ -f $script_loc ]
            then
                continue
            fi
            if [ "$platform" == "Windows" ]
            then
                echo '@echo off' > "../$script"
                echo "%~dp0\\Writing3D\\scripts\\$platform\\$script %*" >> "../$script"
            else
                echo '#!/bin/bash' >> "../$script"
                echo 'if [ ! -z "$BASH_SOURCE" ]' >> "../$script"
                echo 'then' >> "../$script"
                echo '    SCRIPT_NAME="${BASH_SOURCE[0]}"' >> "../$script"
                echo 'else' >> "../$script"
                echo '    SCRIPT_NAME="$0"' >> "../$script"
                echo 'fi' >> "../$script"
                echo 'if command -v readlink > /dev/null 2>&1' >> "../$script"
                echo 'then' >> "../$script"
                echo '    SCRIPT_DIR="$(dirname "$(readlink -f "$SCRIPT_NAME")")"' >> "../$script"
                echo 'else' >> "../$script"
                echo '    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_NAME")" && pwd -P)"' >> "../$script"
                echo 'fi' >> "../$script"
                echo '"$SCRIPT_DIR/Writing3D/scripts/Linux/cwapp.sh" "$@"' >> "../$script"
                chmod +x "../$script"
            fi
        done
        cd $ROOT_DIR
        if [ "$platform" == "Linux" ]
        then
            tar czf "$BUILD_DIR/W3DZip-${platform}-unstable.tar.gz" "W3DZip-$platform"
        else
            zip -r "$BUILD_DIR/W3DZip-${platform}-unstable.zip" "W3DZip-$platform"
        fi
        cd -
    done
}

function push_develop {
    git checkout develop
    git push
}

function build {
    push_develop
    echo "Creating zip installs for each platform..."
    create_platform_specifics
    echo "Sending build to writing3d.xyz host..."
    sync
    echo "Build complete and synced."
}

cd $REPO_DIR
git status
echo "Given the above git status, do you wish to build?"
select yn in "Yes" "No";
do
    case $yn in
        Yes ) build; break;;
        No ) exit;;
    esac
done
