import cv2

#from picamera2 import Picamera2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()


def capture_video_old():

    _, img = cam.read()
    _, frame = cv2.imencode('.jpg', img)
    return frame


def capture_video():

    _, img = picam2.read()
    _, frame = cv2.imencode('.jpg', img)
    return frame
