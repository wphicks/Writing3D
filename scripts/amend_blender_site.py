import site
import os

if __name__ == "__main__":
    w3d_path = os.path.abspath(
        os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir
            )
        )
    )

    all_sites = site.getsitepackages()
    for site_ in all_sites:
        if "site-packages" in os.path.split(site_)[1]:
            with open(os.path.join(site_, "Writing3D.pth"), "w") as pthfile:
                pthfile.write(w3d_path)
