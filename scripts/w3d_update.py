#!/usr/bin/env python
import os
import dulwich.repo
import dulwich.index
import dulwich.client
from dulwich import porcelain

W3D_PATH = os.path.abspath(
    os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir
        )
    )
)

REMOTE_PATH = "https://github.com/wphicks/Writing3D.git"


def update_w3d(branch="master"):
    target_ref = 'refs/heads/{}'.format(branch).encode()
    w3d_repo = dulwich.repo.Repo(W3D_PATH)
    porcelain.reset(w3d_repo, "hard")
    porcelain.pull(W3D_PATH, REMOTE_PATH, target_ref)
    w3d_repo.refs.set_symbolic_ref('HEAD'.encode(), target_ref)
    porcelain.reset(w3d_repo, "hard")


if __name__ == "__main__":
    update_w3d()
