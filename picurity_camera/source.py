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
    width: int = 640
    height: int = 480
    vflip: bool = False
    hflip: bool = False


class SourceError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Source(ABC):
    def __init__(self, config: SourceConfig):
        self.config = config
        pass

    def get_frame(self):
        return self._encode_as_jpg(self._get_frame_raw())

    @staticmethod
    def _encode_as_jpg(img):
        _, frame = cv2.imencode('.jpg', img)
        return frame

    @abstractmethod
    def _get_frame_raw(self):
        pass

    def capture_video(self):
        width = int(self.config.width)
        height = int(self.config.height)
        size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, size)
        try:
            logging.warning("start recording")
            start = time.time()
            while(True):
                frame = self._get_frame_raw()
                out.write(frame)
                if int(time.time()) - start > 5:
                    break
        except Exception:
            pass
        finally:
            logging.warning("done recording")
            out.release()
            cv2.destroyAllWindows()


class WebcamSource(Source):
    def __init__(self, config: SourceConfig):
        super().__init__(config)
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)

    def _get_frame_raw(self):
        _, img = self.cam.read()
        return img


class PicameraSource(Source):
    def __init__(self, config: SourceConfig):
        super().__init__(config)
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

    def _get_frame_raw(self):
        return self.picam2.capture_array()


def source_factory(config) -> Source:
    if picamera_enabled:
        config.vflip = True
        config.hflip = True
        return PicameraSource(config)
    else:
        return WebcamSource(config)
