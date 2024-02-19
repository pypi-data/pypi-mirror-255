from math import sqrt, sin, cos, acos, radians, degrees
from Polygon import Polygon


class Player:
    def __init__(self, x, y, z, h_angle, distance_to_the_screen, screen_width, screen_height):
        # координаты игрока
        self.x = x
        self.y = y
        self.z = z
        self.h_angle = h_angle  # полярный угол игрока относительно OY
        self.distance_to_the_screen = distance_to_the_screen  # константа расстояния до экрана в "тугриках"
        self.screen_W = screen_width  # ширина экрана в "тугриках"
        self.screen_H = screen_height  # высота экрана в "тугриках"
        # уравнение прямой вертикально стоящего экрана
        self.A = None
        self.B = None
        self.C = None
        # уравнение прямой луча зрения
        self.a = None
        self.b = None
        self.c = None

    def set_equations(self):  # сеттер self.a, self.b, self.c, self.A, self.B, self.C
        # координаты(плоскостные) проекции точки камеры на прямую экрана
        x2 = self.x + cos(radians((90 - self.h_angle) % 360)) * self.distance_to_the_screen
        y2 = self.y + sin(radians((90 - self.h_angle) % 360)) * self.distance_to_the_screen
        self.a, self.b, self.c = Polygon.get_direct_equation(self.x, self.y, x2, y2)  # построение прямой по
        # self.x, self.y, x2, y2

        dst = sqrt(self.distance_to_the_screen * self.distance_to_the_screen + self.screen_W * self.screen_W / 4)
        # расстояние до правого края экрана
        angle = (self.h_angle + degrees(acos(self.distance_to_the_screen / dst))) % 360  # полярный угол
        # правого края экрана относительно камеры
        # координаты правого края экрана на плоскости
        x3 = self.x + cos(radians((90 - angle) % 360)) * dst
        y3 = self.y + sin(radians((90 - angle) % 360)) * dst
        self.A, self.B, self.C = Polygon.get_direct_equation(x2, y2, x3, y3)  # построение прямой экрана по его центру
        # и правому краю

    def get_step(self, n):  # делает шаг игроком в сторону луча зрения
        h = radians((90 - self.h_angle) % 360)  # конвертация self.h_angle в стандартный вид
        self.x += cos(h) * n  # сдвиг по OX
        self.y += sin(h) * n  # сдвиг по OY

    def get_vertical_shift(self, n):
        self.z += n

    def rotate(self, angle):  # поворот по горизонтали на угол angle
        self.h_angle = (self.h_angle + angle) % 360
