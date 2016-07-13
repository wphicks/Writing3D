import flask

writer = flask.Flask("W3D Writer")


@writer.route("/")
def main():
    return flask.render_template('index.html')

if __name__ == "__main__":
    writer.run()
