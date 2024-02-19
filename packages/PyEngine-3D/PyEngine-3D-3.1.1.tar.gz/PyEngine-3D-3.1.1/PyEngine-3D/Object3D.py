class Object3D:
    def __init__(self, pol):  # инициаизация
        self.polygons = pol

    def rotate(self, point, flag, angle):  # аналогичен такому же методу в классе Point
        for p in self.polygons:
            p.rotate(point, flag, angle)

    def shift(self, flag, dist):  # аналогичен такому же методу в классе Point
        for p in self.polygons:
            p.shift(flag, dist)

    def zeroing(self):  # обнуление сеттер-счётчиков
        for p in self.polygons:
            p.zeroing()
