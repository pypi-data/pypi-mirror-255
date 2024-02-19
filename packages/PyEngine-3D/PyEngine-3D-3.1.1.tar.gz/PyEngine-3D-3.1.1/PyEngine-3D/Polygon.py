from numba import njit
from pygame import *

from Point import Point
from Constants import CONSTANTS

init()


class Polygon:
    def __init__(self, point1, point2, point3, color=-1,
                 line12_color=(0, 0, 0), line23_color=(0, 0, 0), line13_color=(0, 0, 0),
                 line12_width=0, line23_width=0, line13_width=0):
        # точки полигона
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.color = color  # цвет(прозрачность в случае -1) полигона
        # цвета рёбер полигона
        self.line12_color = line12_color
        self.line23_color = line23_color
        self.line13_color = line13_color
        # толщина рёбер полигона
        self.line12_width = line12_width
        self.line23_width = line23_width
        self.line13_width = line13_width

    def setter1(self, pl):  # первичный сеттер(сеттирует точку только в случае необходимости)
        if self.point1.is_set < 1:
            self.point1.set_is_visible(pl)
            self.point1.is_set = 1
        if self.point2.is_set < 1:
            self.point2.set_is_visible(pl)
            self.point2.is_set = 1
        if self.point3.is_set < 1:
            self.point3.set_is_visible(pl)
            self.point3.is_set = 1

    def setter2(self, pl):  # вторичный сеттер(сеттирует точку только в случае необходимости)
        if self.point1.is_set < 2:
            self.point1.set_distance(pl)
            self.point1.set_angles(pl)
            self.point1.set_coords_on_screen(pl)
            self.point1.is_set = 2
        if self.point2.is_set < 2:
            self.point2.set_distance(pl)
            self.point2.set_angles(pl)
            self.point2.set_coords_on_screen(pl)
            self.point2.is_set = 2
        if self.point3.is_set < 2:
            self.point3.set_distance(pl)
            self.point3.set_angles(pl)
            self.point3.set_coords_on_screen(pl)
            self.point3.is_set = 2

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_direct_equation(x1, y1, x2, y2):  # даёт уравнение прямой по 2 точкам на плоскости
        if y1 == y2:
            return 0, 1, -y1
        b = (x1 - x2) / (y2 - y1)
        c = -(x1 + b * y1)
        return 1, b, c

    @staticmethod
    def get_plane_segment_intersection(point1, point2, pl):  # выдаёт точку перечения отрезка с вертикальной плоскостью
        if point1.z > point2.z:  # свап точек, если первая выше второй
            point1, point2 = point2, point1
        a, b, c = Polygon.get_direct_equation(point1.x, point1.y, point2.x, point2.y)  # уравнение прямой, которой
        # принадлежит отрезок при "виде сверху"
        x, y = Point.get_directs_intersection(a, b, c, pl.A, pl.B, pl.C)  # нахождение плоскостных координат
        # вертикали пересечения
        dst = Point.get_dist(point1.x, point1.y, point2.x, point2.y)  # плоскостная длина отрезка
        sub_dst = Point.get_dist(point1.x, point1.y, x, y)  # расстояние от первой точки до её проекции на вертикаль
        z = point1.z + (point2.z - point1.z) * (sub_dst / dst)  # нахождение z-координаты точки пересечения
        point3 = Point(x, y, z)  # создание объекта точки пересечения
        point3.is_visible = True  # первичный сеттинг точки пересечения
        return point3

    def get_clipped(self, pl):  # клиппинг(обрезка) данного полигона
        if self.point1.is_visible == self.point2.is_visible == self.point3.is_visible:
            # обработка случая, когда все точки по одну сторону от экрана
            if self.point1.is_visible:
                return [self]
            else:
                return -1
        else:
            p1, p2, p3 = sorted([self.point1, self.point2, self.point3], key=lambda s: s.is_visible)  # в [p1, p2, p3]
            # в начале идут невидимые, а потом видимые точки
            if p2.is_visible:  # обработка случая, когда [p1.is_visible,p2.is_visible,p3.is_visible] = [False,True,True]
                # точки пересечения полигона с плоскостью экрана
                p12 = self.get_plane_segment_intersection(p1, p2, pl)
                p13 = self.get_plane_segment_intersection(p1, p3, pl)
                return [Polygon(p12, p2, p3, self.color, self.line12_color, self.line23_color, self.color,
                                self.line12_width, self.line23_width, 0),
                        Polygon(p13, p12, p3, self.color, self.color, self.color, self.line13_color, 0, 0,
                                self.line13_width)]  # возврат 2 полигонов, полученных разрезанием 4-угольника
            else:  # обработка случая, когда [p1.is_visible, p2.is_visible, p3.is_visible] = [False, False, True]
                # точки пересечения полигона с плоскостью экрана
                p23 = self.get_plane_segment_intersection(p2, p3, pl)
                p13 = self.get_plane_segment_intersection(p1, p3, pl)
                return [Polygon(p13, p23, p3, self.color, self.color, self.line23_color, self.line13_color,
                                0, self.line23_width, self.line13_width)]  # возврат полигона, построенного по 3 точкам

    def draw_polygon(self, sc, pl):
        w, h = sc.get_size()  # высота и ширина экрана в пикселях
        coords1 = self.point1.coords_on_screen  # координаты self.point1 в "тугриках", где O = [центр экрана]
        coords1 = (int((coords1[0] / pl.screen_W + 0.5) * w), int((-coords1[1] / pl.screen_H + 0.5) * h))  # конвертация
        # coords1 для конечной отрисовки

        coords2 = self.point2.coords_on_screen  # координаты self.point2 в "тугриках", где O = [центр экрана]
        coords2 = (int((coords2[0] / pl.screen_W + 0.5) * w), int((-coords2[1] / pl.screen_H + 0.5) * h))  # конвертация
        # coords2 для конечной отрисовки

        coords3 = self.point3.coords_on_screen  # координаты self.point3 в "тугриках", где O = [центр экрана]
        coords3 = (int((coords3[0] / pl.screen_W + 0.5) * w), int((-coords3[1] / pl.screen_H + 0.5) * h))  # конвертация
        # coords3 для конечной отрисовки

        # нахождение толщин рёбер полигона
        width12 = int(CONSTANTS.CONSTANT_DISTANCE / ((self.point1.distance+self.point2.distance)/2) * self.line12_width)
        width23 = int(CONSTANTS.CONSTANT_DISTANCE / ((self.point2.distance+self.point3.distance)/2) * self.line23_width)
        width13 = int(CONSTANTS.CONSTANT_DISTANCE / ((self.point1.distance+self.point3.distance)/2) * self.line13_width)
        if self.color != -1:  # закрашивание треугольника полигона на экране в случае его непрозрачности
            draw.polygon(sc, self.color, [coords1, coords2, coords3])
        # отрисовка рёбер полигона
        draw.line(sc, self.line12_color, coords1, coords2, width12)
        draw.line(sc, self.line23_color, coords2, coords3, width23)
        draw.line(sc, self.line13_color, coords1, coords3, width13)

    def rotate(self, point, flag, angle):  # аналогичен такому же методу в классе Point
        self.point1.rotate(point, flag, angle)
        self.point2.rotate(point, flag, angle)
        self.point3.rotate(point, flag, angle)

    def shift(self, flag, n):  # аналогичен такому же методу в классе Point
        self.point1.shift(flag, n)
        self.point2.shift(flag, n)
        self.point3.shift(flag, n)

    def zeroing(self):  # обнуление сеттер-счётчиков
        self.point1.is_set = 0
        self.point2.is_set = 0
        self.point3.is_set = 0
