from abc import ABC, abstractmethod
from dataclasses import dataclass


import logging
import cv2

picamera_enabled = False

try:
    #    my_module = importlib.import_module('os.path')
    from picamera2 import Picamera2
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


class Source(ABC):
    @abstractmethod
    def __init__(self, config: SourceConfig):
        pass

    @abstractmethod
    def get_frame(self):
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


def source_factory(config) -> Source:
    config = SourceConfig()
    if picamera_enabled:
        config.vflip = True
        config.hflip = True
        return PicameraSource(config)
    else:
        return WebcamSource(config)
