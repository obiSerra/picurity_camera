import cv2

from picamera2 import Picamera2
import libcamera

#cam = cv2.VideoCapture(0)
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


picam2 = Picamera2()
capture_config = picam2.create_still_configuration(
    main={"format": 'XRGB8888',
          "size": (640, 480)
})
capture_config["transform"] = libcamera.Transform(hflip=1, vflip=1)

picam2.configure(capture_config)
picam2.start()


def capture_video_old():
    pass
 #   _, img = cam.read()
 #   _, frame = cv2.imencode('.jpg', img)
  #  return frame


def capture_video():
    img = picam2.capture_array()
    _, frame = cv2.imencode('.jpg', img)
    return frame
