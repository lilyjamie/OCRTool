import cv2
import random
import platform
import os


class CameraPicture:
    def __init__(self, camera_port):
        self.camera_port = camera_port

    def get_camera(self, width=1920, height=1080):
        if "Windows" == platform.system():
            self.cap = cv2.VideoCapture(self.camera_port + cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(self.camera_port)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        if self.cap.isOpened():
            for i in range(3):
                self.cap.read()
            self.ret, self.origin_frame = self.cap.read()
            if not os.path.isdir(r"PictureStore"):
                os.makedirs(r"PictureStore")
            picture_name = "PictureStore/" + "".join(random.sample("qwertyuiopasdfghjklzxcvbnm", 5)) + ".jpg"
            cv2.imwrite(picture_name, self.origin_frame)
            return picture_name

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
