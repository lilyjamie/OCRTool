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

