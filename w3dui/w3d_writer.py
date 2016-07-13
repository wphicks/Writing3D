import flask
import webbrowser
import threading

writer = flask.Flask("W3D Writer")


class EditorTab(object):
    """Top-level tab for W3D Writer"""
    def __init__(self, name):
        self.name = name


@writer.route("/")
def main():
    return flask.render_template(
        'index.html',
        toptabs=[
            EditorTab("Global"),
            EditorTab("Objects"),
            EditorTab("Timelines")
        ]
    )

if __name__ == "__main__":
    server_thread = threading.Thread(target=writer.run)
    server_thread.start()
    webbrowser.open_new_tab("http://localhost:5000")
