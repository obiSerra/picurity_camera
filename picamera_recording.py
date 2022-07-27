from threading import Thread
import cv2
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import libcamera


class PicameraVideoStream:
    def __init__(self, src=0):
        self.picam2 = Picamera2()
        capture_config = self.picam2.create_video_configuration(
            main={"format": 'XRGB8888',
                  "size": (640, 480)})
        capture_config["transform"] = libcamera.Transform(
            hflip=int(1),
            vflip=int(1)
        )

        self.picam2.configure(capture_config)
        self.picam2.start()
        time.sleep(2)

        self.frame = self.picam2.capture_array()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.recording = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def start_recording(self):

        width = int(640)
        height = int(480)
        size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output.avi', fourcc, 20.0, size)
        self.recording = True

    def stop_recording(self):
        self.out.release()
        self.recording = False

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            self.frame = self.picam2.capture_array()
            if self.recording:
                self.out.write(self.frame)

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


if __name__ == "__main__":
    web = PicameraVideoStream()
    web.start()
    time.sleep(2)
    web.start_recording()
    time.sleep(5)
    web.stop_recording()
    web.stop()
