from .ObserverSubject import Subject


class PicturePathObserver(Subject):
    def __init__(self, picture_path):
        super(PicturePathObserver, self).__init__()
        self._picture_path = picture_path

    @property
    def picture_path(self):
        return self._picture_path

    @picture_path.setter
    def picture_path(self, pic_path):
        self._picture_path = pic_path
        self.notify()
