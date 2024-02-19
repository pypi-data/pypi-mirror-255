from numba import njit
from math import sqrt, sin, cos, tan, asin, radians, degrees


class Point:
    def __init__(self, x, y, z):
        # координаты точки
        self.x = x
        self.y = y
        self.z = z
        self.distance = None  # расстояние от точки до камеры
        self.h_angle = None  # полярный угол точки относительно камеры(по плоскости XY)
        self.v_angle = None  # полярный угол точки относительно камеры(по плоскости TZ, где T - луч зрения)
        self.is_visible = None  # попадает ли точка в заэкранное полупространство
        self.coords_on_screen = None  # координаты точки на экране(в "тугриках")
        self.is_set = 0  # степень актуальности вышеперечисленных пременных(сколько раз вызывались сеттеры за этот кадр)

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_perpendicular(a, b, c, x, y):  # выдаёт уравнение прямой, препендикулярной данной и проходящей через (x, y)
        return -b, a, b * x - a * y

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def is_behind_direct(x, y, px, py, a, b, c):  # верно ли, что точки (x, y) и (px, py)
        # лежат по разные стороны от прямой
        val = a * x + b * y + c  # значение выражения при подстановке точки (x, y)
        valp = a * px + b * py + c  # значение выражения при подстановке точки (px, py)
        return (val > 0) != (valp > 0) or abs(val) < 0.001

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_directs_intersection(a1, b1, c1, a2, b2, c2):  # выдаёт точку пересечения 2 прямых
        k = a1 * b2 - b1 * a2
        if k == 0:
            return 1e18, 1e18
        return (b1 * c2 - b2 * c1) / k, (a2 * c1 - a1 * c2) / k

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_dist(x1, y1, x2, y2):  # выдаёт расстояние между 2 точками на плоскости по теореме Пифагора
        return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_dist3D(x1, y1, z1, x2, y2, z2):  # выдаёт расстояние между точками в пространстве по теореме Пифагора
        dx = abs(x1 - x2)  # Δx
        dy = abs(y1 - y2)  # Δy
        dz = abs(z1 - z2)  # Δz
        return sqrt(dx * dx + dy * dy + dz * dz)

    def get_distance(self, p):  # выдаёт расстояние от этой точки до другой точки/камеры по теореме Пифагора в 3D
        return self.get_dist3D(self.x, self.y, self.z, p.x, p.y, p.z)

    def set_distance(self, pl):  # сеттер self.distance
        self.distance = self.get_distance(pl)
        return self.distance

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_angle(x, y):  # выдаёт полярный угол точки на плоскости относительно (0, 0)
        if (x, y) == (0, 0):  # обработка частного случая
            return 0
        d = sqrt(x * x + y * y)  # расстояние до (0, 0)
        if x >= 0:
            return 90 - degrees(asin(y / d))
        else:
            return 270 + degrees(asin(y / d))

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_point(angle, dist):  # возвращает координаты точки, полярный угол(отсчёт от OY по часовой стрелке)
        # которой относительно точки (0, 0) равен angle, а расстояние до (0, 0) равно dist≥0
        if dist == 0:
            return 0, 0
        newangle = radians(360 - (angle + 270) % 360)  # пересчёт угла в стандартный вид
        y = dist * sin(newangle)
        x = dist * cos(newangle)
        return x, y

    def get_angles(self, pl):  # выдаёт полярные углы точки относительно камеры
        dx = self.x - pl.x  # Δx
        dy = self.y - pl.y  # Δy
        dz = self.z - pl.z  # Δz
        angle_h = self.get_angle(dx, dy)  # установка полярного угла точки относительно камеры(по плоскости XY)
        # установкка полярного угла точки относительно камеры(по плоскости TZ, где T - луч зрения)
        a2, b2, c2 = self.get_perpendicular(pl.a, pl.b, pl.c, self.x, self.y)  # прямая, перпендикулярная
        # прямой зрения, проходящая через данную точку(на плоскости)
        x, y = self.get_directs_intersection(pl.a, pl.b, pl.c, a2, b2, c2)  # координаты(на плоскости XY) проекции
        # данной точки на плоскость TZ
        dst = self.get_dist(x, y, pl.x, pl.y)  # расстояние от камеры до вертикальной прямой (x, y)
        if abs(self.get_angle(x - pl.x, y - pl.y) - pl.h_angle) > 0.00001:  # располагается ли точка (x, y) "позади"
            # камеры (с учётом небольшой погрешности)
            dst = -dst
        angle_v = self.get_angle(dz, dst)
        return angle_h, angle_v

    def set_angles(self, pl):  # сеттер self.h_angle и self.v_angle
        self.h_angle, self.v_angle = self.get_angles(pl)
        return self.h_angle, self.v_angle

    def set_is_visible(self, pl):  # сеттер self.is_visible
        self.is_visible = self.is_behind_direct(self.x, self.y, pl.x, pl.y, pl.A, pl.B, pl.C)
        return self.is_visible

    @staticmethod
    @njit(fastmath=True, nogil=True, cache=True)
    def get_coord_at_plane(pl_angle, self_angle, dist):  # X-координата точки на экране при 2.5D в "тугриках"
        radian_distance = abs(pl_angle - self_angle)   # предпогаемое угловое расстояние
        angle = min(radian_distance, 360 - radian_distance)  # угловое расстояние(по модулю)
        d = tan(radians(angle)) * dist  # X-координата точки на экране при 2.5D по модулю
        if abs((self_angle + angle) % 360 - pl_angle) < 0.001:  # "размодуляция" d
            return -d
        return d

    def get_coords_on_screen(self, pl):  # координаты точки на экране в "тугриках"(точка (0, 0) в центре экрана) в 3D
        x = self.get_coord_at_plane(pl.h_angle, self.h_angle, pl.distance_to_the_screen)
        y = self.get_coord_at_plane(0, self.v_angle, pl.distance_to_the_screen)
        return x, y

    def set_coords_on_screen(self, pl):  # сеттер self.coords_on_screen
        self.coords_on_screen = self.get_coords_on_screen(pl)
        return self.coords_on_screen

    def rotate(self, point, flag, angle):  # поворачивает нашу точку относительно точки point(кортеж) на угол angle
        x, y, z = point
        if flag == 'OX':
            newangle = (self.get_angle(self.y - y, self.z - z) + angle) % 360  # пересчёт нового угла
            new_dy, new_dz = self.get_point(newangle, self.get_dist(y, z, self.y, self.z))  # пересчёт новых
            # Δx, Δy, Δz
            self.y, self.z = y + new_dy, z + new_dz
        elif flag == 'OY':
            newangle = (self.get_angle(self.z - z, self.x - x) + angle) % 360  # пересчёт нового угла
            new_dz, new_dx = self.get_point(newangle, self.get_dist(z, x, self.z, self.x))  # пересчёт новых
            # Δx, Δy, Δz
            self.z, self.x = z + new_dz, x + new_dx
        else:
            newangle = (self.get_angle(self.x - x, self.y - y) + angle) % 360  # пересчёт нового угла
            new_dx, new_dy = self.get_point(newangle, self.get_dist(x, y, self.x, self.y))  # пересчёт новых
            # Δx, Δy, Δz
            self.x, self.y = x + new_dx, y + new_dy

    def shift(self, flag, n):  # делает сдвиг очки по одной из осей координат на n шагов
        if flag == 'OX':
            self.x += n
        elif flag == 'OY':
            self.y += n
        else:
            self.z += n
