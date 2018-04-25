from math import copysign


class SPN:
    def __init__(self, spn):
        self.lon = None
        self.lat = None
        self.set_spn(spn)
        self.move_shift = 5
        self.scale_shift = 2    # Коэффициент изменения масштаба
        self.min_scale = 0.001  # (чем больше это значение, тем больше нажатий он игнорирует)
        self.max_scale = 35

    def set_spn(self, spn):
        if type(spn) is str:
            self.lon, self.lat = map(lambda x: float(x), spn.split(","))
        elif type(spn) in (tuple, list):
            if all(map(lambda x: type(x) is float, spn)):
                self.lon, self.lat = spn

    def get_spn(self, mode="str"):
        if mode == "str":
            return str(self.lon) + "," + str(self.lat)
        elif mode == "float":
            return self.lon, self.lat

    def move(self, point_ll, axis, move_dir):
        p_lon, p_lat = map(lambda x: float(x), point_ll.split(","))
        shift = (self.lon + self.lat) / 2 / self.move_shift * copysign(1, move_dir)
        if axis == "v":
            p_lat += shift
        elif axis == "h":
            p_lon += shift

        return str(p_lon) + "," + str(p_lat)

    def change_scale(self, scale_dir):            # <<<===  Смотреть сюда
        shift = copysign(1, scale_dir) / self.scale_shift

        new_lon = self.lon * (1 + shift)  # lon + lon / shift         \
        if new_lon < self.min_scale:      # #                          }=> lon + lon * shift = lon * (1 + shift)
            self.lon = self.min_scale     # shift = +-1 / scale_shift /                          (за скобку)
        elif new_lon > self.max_scale:         # (обратная дробь)
            self.lon = self.max_scale
        else:
            self.lon = round(new_lon, 10)  # Округляю на всякий случай

        new_lat = self.lat * (1 + shift)
        if new_lat < self.min_scale:
            self.lat = self.min_scale
        elif new_lat > self.max_scale:
            self.lat = self.max_scale
        else:
            self.lat = round(new_lat, 10)

        print("shift : {}\n"
              "lon   : {}\n"
              "lat   : {}".format(shift, self.lon, self.lat))
