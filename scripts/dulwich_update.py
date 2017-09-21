#!/usr/bin/env python3

import urllib.request
import os
import zipfile
import subprocess
import shutil
import pyw3d


INSTALL_PATH = os.path.abspath(
    os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir
        )
    )
)


def update_dulwich():
    try:
        import dulwich.repo
        from dulwich import porcelain
    except ImportError:
        install_dulwich()
        return
    try:
        dulwich_repo = dulwich.repo.Repo(
            os.path.join(INSTALL_PATH, "dulwich")
        )
    except dulwich.errors.NotGitRepository:
        shutil.rmtree(os.path.join(INSTALL_PATH, "dulwich"))
        dulwich_repo = porcelain.clone(
            "https://github.com/jelmer/dulwich.git",
            os.path.join(INSTALL_PATH, "dulwich")
        )
    porcelain.reset(dulwich_repo, "hard")
    porcelain.pull(
        dulwich_repo, remote_location="https://github.com/jelmer/dulwich.git"
    )
    install_dulwich()


def apply_shim(setup_filename):
    new_content = []
    shim_content = []
    shim_path = os.path.abspath(
        os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "dulwich_shim.py"
            )
        )
    )
    with open(shim_path, 'r') as shim_file:
        shim_content.extend(shim_file)

    with open(setup_filename, 'r') as setup_file:
        for line in setup_file:
            new_content.append(line)
            if line.startswith("#!"):
                new_content.extend(shim_content)

    with open(setup_filename, 'w') as setup_file:
        setup_file.write("".join(new_content))


def install_dulwich():
    if not os.path.isdir(os.path.join(INSTALL_PATH, "dulwich")):
        dulwich_filename, headers = urllib.request.urlretrieve(
            "https://github.com/jelmer/dulwich/archive/master.zip"
        )
        dulwich_zip = zipfile.ZipFile(dulwich_filename)
        dulwich_zip.extractall(path=INSTALL_PATH)

        os.rename(
            os.path.join(INSTALL_PATH, "dulwich-master"),
            os.path.join(INSTALL_PATH, "dulwich")
        )

    setup_filename = os.path.join(INSTALL_PATH, "dulwich", "setup.py")

    apply_shim(setup_filename)

    subprocess.call(
        [
            pyw3d.BLENDER_EXEC, "--background", "--python",
            setup_filename, "--", "--pure", "install", "--force"
        ]
    )


if __name__ == "__main__":
    update_dulwich()
