from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
from datetime import datetime


import logging
import cv2

picamera_enabled = False

try:
    #    my_module = importlib.import_module('os.path')
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FfmpegOutput
    import libcamera
    picamera_enabled = True
except ModuleNotFoundError as e:
    logging.warning(e)


@dataclass
class SourceConfig:
    width: int = 320
    height: int = 240
    vflip: bool = False
    hflip: bool = False


class SourceError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Source(ABC):
    @abstractmethod
    def __init__(self, config: SourceConfig):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def capture_video(self):
        pass

    @staticmethod
    def _encode_as_jpg(img):
        _, frame = cv2.imencode('.jpg', img)
        return frame


class WebcamSource(Source):
    def __init__(self, config: SourceConfig):
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)

    def get_frame(self):
        _, img = self.cam.read()
        return self._encode_as_jpg(img)

    def capture_video(self):
        logging.error("capture_video not supported by WebcamSource")
        raise(SourceError("capture_video not supported by WebcamSource"))


class PicameraSource(Source):
    def __init__(self, config: SourceConfig):
        self.picam2 = Picamera2()
        capture_config = self.picam2.create_still_configuration(
            main={"format": 'XRGB8888',
                  "size": (config.width, config.height)})
        capture_config["transform"] = libcamera.Transform(
            hflip=int(config.hflip),
            vflip=int(config.vflip)
        )

        self.picam2.configure(capture_config)
        self.picam2.start()

    def get_frame(self):
        img = self.picam2.capture_array()
        return self._encode_as_jpg(img)

    def capture_video(self, video_name=""):
        video_config = self.picam2.create_video_configuration()
        self.picam2.configure(video_config)

        encoder = H264Encoder(10000000)
        output = FfmpegOutput(f"video_name={datetime.now()}.mp4")

        self.picam2.start_recording(encoder, output)
        time.sleep(10)
        self.picam2.stop_recording()


def source_factory(config) -> Source:
    config = SourceConfig()
    if picamera_enabled:
        config.vflip = True
        config.hflip = True
        return PicameraSource(config)
    else:
        return WebcamSource(config)
