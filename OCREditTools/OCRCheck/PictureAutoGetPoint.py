import cv2


class PictureGetPoint:
    def __init__(self, picture_way):
        self.picture_way = picture_way
        self.start_x_point, self.start_y_point, self.end_x_point, self.end_y_point = -1, -1, -1, -1
        self.point = (self.start_x_point, self.start_y_point, self.end_x_point, self.end_y_point)
        self.point_list = []
        self.flag = True
        self.camera_flag = False
        self.right_button_down_count = 0
        if ":" in str(self.picture_way):
            self.get_picture()
        else:
            self.camera_flag = True
            self.get_camera()

    def get_picture(self):
        origin_img = cv2.imread(self.picture_way)
        self.img = cv2.resize(origin_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)


    def get_camera(self):
        self.cap = cv2.VideoCapture(self.picture_way + cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        if self.cap.isOpened():
            for i in range(3):
                self.cap.read()
            self.ret, self.origin_frame = self.cap.read()
            self.frame = cv2.resize(self.origin_frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imwrite("pic.jpg", self.frame)

    def on_mouse(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            self.start_x_point = x
            self.start_y_point = y

        elif event == cv2.EVENT_LBUTTONUP:
            self.end_x_point = x
            self.end_y_point = y
            cv2.rectangle(param, (self.start_x_point, self.start_y_point), (self.end_x_point, self.end_y_point),
                          (255, 0, 0), thickness=1, lineType=8)
            if self.start_y_point == self.end_y_point:
                pass
            else:
                if self.camera_flag:
                    self.point = [self.start_x_point, self.start_y_point, self.end_x_point, self.end_y_point]
                else:
                    self.point = [self.start_x_point*2, self.start_y_point*2, self.end_x_point*2, self.end_y_point*2    ]
                self.point_list.append(self.point)
                if len(self.point_list) > 1:
                    self.point_list.pop(0)

    def show(self):
        if self.camera_flag:
            # cv2.namedWindow("image",0),可以用cv2.resizeWindow()函数调整窗口大小
            cv2.namedWindow("image")
            self.img = cv2.imread("pic.jpg")
            while True:
                cv2.setMouseCallback("image", self.on_mouse, self.img)
                cv2.imshow('image', self.img)
                k = cv2.waitKey(1000) & 0xFF
                if k == ord("q"):
                    self.cap.release()
                    cv2.destroyWindow('image')
                    break

                elif k == ord("r"):
                    self.point_list = []
                    cv2.destroyWindow('image')
                    cv2.namedWindow("image")
                    self.img = cv2.imread("pic.jpg")
                    cv2.setMouseCallback("image", self.on_mouse, self.img)
                    cv2.imshow("image", self.img)
        else:
            cv2.namedWindow("image")
            while True:
                cv2.setMouseCallback("image", self.on_mouse, self.img)
                cv2.imshow('image', self.img)
                k = cv2.waitKey(1000) & 0xFF
                if k == ord("q"):
                    cv2.destroyWindow('image')
                    break

                elif k == ord("r"):
                    self.point_list = []
                    cv2.destroyWindow('image')
                    cv2.namedWindow("image")
                    origin_img = cv2.imread(self.picture_way)
                    self.img = cv2.resize(origin_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                    cv2.setMouseCallback("image", self.on_mouse, self.img)
                    cv2.imshow("image", self.img)

    def __del__(self):
        if self.camera_flag:
            self.cap.release()
        cv2.destroyAllWindows()




