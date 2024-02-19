class Map:
    def __init__(self, objects):
        self.polygons = list()
        for obj in objects:  # объявление полигонов карты
            self.polygons += obj.polygons

    def first_set_polygons(self, pl):  # первый сеттинг
        for p in self.polygons:
            p.setter1(pl)

    def clip_polygons(self, pl):  # обрезка полигонов плоскостью экрана-оставление в массиве только передэкранной части
        pol = list()
        for p in self.polygons:
            new = p.get_clipped(pl)
            if new != -1:
                pol += new
        self.polygons = pol

    def second_set_polygons(self, pl):  # второй сеттинг
        for p in self.polygons:
            p.setter2(pl)

    def sort_polygons(self):  # сортировка полигонов для отрисовки алгоритмом художника
        self.polygons.sort(key=lambda p: p.point1.distance + p.point2.distance + p.point3.distance, reverse=True)

    def draw_polygons(self, pl, sc):  # отрисовка полигонов на экране
        for p in self.polygons:
            p.draw_polygon(sc, pl)

    @staticmethod
    def paint_world_map(m, pl, sc, bg):  # главная функция отрисовки кадра - передаётся ссылка на внешний массив
        wmap = Map(m)  # конвертация массива объектов m в объект класса Map, временный объект
        pl.set_equations()  # сеттинг игрока
        wmap.first_set_polygons(pl)  # первый сеттинг
        wmap.clip_polygons(pl)  # оставление в массиве только полигонов, которые перед плоскостью экрана
        # и клиппинг(обрезка) полигонов, пересекающих её
        wmap.second_set_polygons(pl)  # второй сеттинг
        wmap.sort_polygons()  # сортировка полигонов для решения проблемы видимости-прекрывания
        sc.fill(bg)  # закраска предыдущего кадра
        wmap.draw_polygons(pl, sc)  # отрисовка полигонов на экране
        for p in m:  # обнуление сеттер-счётчиков объектов
            p.zeroing()
