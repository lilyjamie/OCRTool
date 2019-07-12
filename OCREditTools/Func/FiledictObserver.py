class Subject(object):
    def __init__(self):
        self._observers = []

    # 添加依赖的对象
    def attach(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)

    # 取消添加
    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    # 这里只是通知上面注册的依赖对象新的变化
    def notify(self, modifier=None):
        for observer in self._observers:
            # 可以设置过滤条件，对不符合过滤条件的更新
            if modifier != observer:
                observer.update(self)


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
