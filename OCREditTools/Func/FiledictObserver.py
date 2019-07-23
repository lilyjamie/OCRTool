from .ObserverSubject import Subject


class File(Subject):
    def __init__(self, file_dict):
        super(File, self).__init__()
        self._file_dict = file_dict

    @property
    def file_dict(self):
        return self._file_dict

    @file_dict.setter
    def file_dict(self, dic):
        self._file_dict = dic
        self.notify()

    def add(self, key, value):
        self.file_dict[key] = value
        self.notify()

    def delete(self, key):
        self.file_dict.pop(key)
        self.notify()

    # 更换key名
    def change_key(self, key, new_key):
        self.file_dict[new_key] = self.file_dict[key]
        self.file_dict.pop(key)
        self.notify()

    # 更换value
    def change_value(self, key, value):
        self.file_dict[key] = value
        self.notify()
