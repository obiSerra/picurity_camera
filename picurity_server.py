#!/usr/bin/python3

from flask import Flask


app = Flask(__name__)


@app.route("/")         # This is our default handler, if no path is given
def index():
    return "hello"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
