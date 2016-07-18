import flask
import webbrowser
import threading
from form_generator import generate_form_class
from pyw3d.project import W3DProject
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

writer = flask.Flask("W3D Writer")


class EditorTab(object):
    """Top-level tab for W3D Writer"""
    def __init__(self, name):
        self.name = name


@writer.route("/")
def main():
    project = W3DProject()
    form = generate_form_class(project)()
    return flask.render_template(
        'index.html',
        toptabs=[
            EditorTab("Global"),
            EditorTab("Objects"),
            EditorTab("Timelines")
        ],
        form=form
    )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # writer.run()
    server_thread = threading.Thread(target=writer.run)
    server_thread.start()
    webbrowser.open_new_tab("http://localhost:5000")
