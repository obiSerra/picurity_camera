#!/usr/bin/python3
import time
import numpy as np
#import matplotlib.pyplot as plt
import cv2
from flask import Flask, Response
from flask import Flask
from flask import render_template

from picurity_camera.source import source_factory, SourceConfig, SourceError

app = Flask(__name__)


source = source_factory(SourceConfig())


def gather_img():
    while True:
        time.sleep(0.1)
        frame = source.get_frame()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')


@app.route('/capture')
def capture():
    try:
        source.capture_video()
    except SourceError as e:
        return "ERROR " + e.message
    return "OK"


@app.route("/mjpeg")
def mjpeg():
    return Response(gather_img(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/")         # This is our default handler, if no path is given
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, threaded=True)
