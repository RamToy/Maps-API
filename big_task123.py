import os
import requests
from GUI import *
from PIL import Image
import pygame
from io import BytesIO


def convert_bytes(bytes_stream):
    image = Image.open(BytesIO(bytes_stream)).convert("RGB")
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.frombuffer(data, size, mode)


class Maps:
    def __init__(self):
        self.lon = "52.376552"
        self.lat = "5.198308"
        self.mode = "sat,skl"
        self.z = "4"
        self.map_image = None
        self.mark_coords = None
        self.search_request = ""
        self.bg_color = 45, 20, 15
        self.fg_color = 245, 250, 115

    def static_request(self):
        static_api_server = "https://static-maps.yandex.ru/1.x/"
        params = {
            "l": self.mode,
            "ll": ",".join([self.lon, self.lat]),
            "z": self.z
        }
        if self.mark_coords is not None:
            params["pt"] = ",".join([self.mark_coords, "pm2vvm"])

        try:
            response = requests.get(static_api_server, params=params)
            if not response:
                return error
            return convert_bytes(response.content)
        except:
            return error

    def geocoder_request(self):
        geocode_api_server = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "geocode": self.search_request,
            "format": "json"
        }
        try:
            response = requests.get(geocode_api_server, params=params)
            if not response:
                return "Не удалось выполнить запрос"
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            self.lon, self.lat = toponym["Point"]["pos"].split()
            self.mark_coords = ",".join([self.lon, self.lat])
            return toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        except IndexError:
            return "Результатов не найдено"
        except:
            return "Проверьте наличие сети Интернет"

    def change_mode(self, direction):
        modes = ["map", "sat", "sat,skl"]
        mode_index = modes.index(self.mode) + direction
        if mode_index > 2:
            mode_index = 0
        elif mode_index < 0:
            mode_index = 2
        self.mode = modes[mode_index]

    def main(self):
        clock = pygame.time.Clock()
        pygame.key.set_repeat(500, 10)

        gui = GUI()

        search_textbox = TextBox((35, 35, 754, 50), -1, (200, 200, 0))
        search_button = ImageButton((803, 23, 74, 74), (255, 150, 25), loop, True)
        status_bar = Label((50, 120, 800, 80), (85, 30, 20), "Введите поисковый запрос", (200, 200, 0), True)

        left_mode = ImageButton((645, 320, 34, 54), self.fg_color, left_arrow, True)
        right_mode = ImageButton((851, 320, 34, 54), self.fg_color, right_arrow, True)
        current_mode = Label((689, 320, 152, 54), self.fg_color, self.mode, self.bg_color, True)

        reset_button = ImageButton((725, 220, 80, 80), self.fg_color, cross, True)

        gui.add_element(search_button)
        gui.add_element(left_mode)
        gui.add_element(right_mode)
        gui.add_element(current_mode)
        gui.add_element(search_textbox)
        gui.add_element(status_bar)
        gui.add_element(reset_button)

        self.map_image = self.static_request()

        running = True
        press_left = False
        press_right = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN and event.key in \
                   [pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:

                    if event.key == pygame.K_PAGEUP and int(self.z) < 17:
                        self.z = str(int(self.z) + 1)
                    elif event.key == pygame.K_PAGEDOWN and int(self.z) > 2:
                        self.z = str(int(self.z) - 1)

                    shift = {"1": 30, "2": 25, "3":20, "4":15, "5": 8,
                             "6": 4, "7": 2, "8": 1, "9": 0.5,
                             "10": 0.25, "11": 0.1, "12": 0.05, "13": 0.025,
                             "14": 0.01, "15": 0.005, "16": 0.0025, "17": 0.001}
                    if event.key == pygame.K_LEFT and float(self.lon) > 1:
                        self.lon = str(float(self.lon) - shift[self.z])
                    elif event.key == pygame.K_RIGHT and float(self.lon) < 179:
                        self.lon = str(float(self.lon) + shift[self.z])

                    if event.key == pygame.K_DOWN and float(self.lat) > -89:
                        self.lat = str(float(self.lat) - shift[self.z])
                    elif event.key == pygame.K_UP and float(self.lat) < 89:
                        self.lat = str(float(self.lat) + shift[self.z])

                    self.map_image = self.static_request()

                gui.get_event(event)

            gui.update()

            screen.fill(self.bg_color)
            # Отрисовка карты с рамкой
            screen.fill(self.fg_color, (10, 220, 620, 470))
            screen.blit(self.map_image, (20, 230))
            # Отрисовка поисковой строки
            screen.fill((233, 230, 0), (20, 20, 860, 80))
            screen.fill((85, 30, 20), (30, 30, 764, 60))
            # Отрисовка статусбара
            screen.fill((233, 230, 0), (45, 115, 810, 90))
            # Отрисовка итерфейса
            gui.render(screen)

            pygame.display.flip()
            clock.tick(60)

            if left_mode.pressed and not press_left:
                self.change_mode(-1)
                current_mode.text = self.mode
                self.map_image = self.static_request()
                press_left = True
            elif not left_mode.pressed and press_left:
                press_left = False
            if right_mode.pressed and not press_right:
                self.change_mode(1)
                current_mode.text = self.mode
                self.map_image = self.static_request()
                press_right = True
            elif not right_mode.pressed and press_right:
                press_right = False

            if search_button.pressed:
                search_textbox.done = True

            elif reset_button.pressed:
                self.mark_coords = None
                self.search_request = ""
                status_bar.set_font_size(-1)
                status_bar.text = "Введите поисковый запрос"
                self.map_image = self.static_request()

            if search_textbox.done and search_textbox.text:
                self.search_request = search_textbox.text
                status_bar.set_font_size(-1)
                status_bar.text = self.geocoder_request()
                self.map_image = self.static_request()

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 700))

    def load_image(name, colorkey=None):
        fullname = os.path.join("data", name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as err:
            print("Cannot load file", name)
            raise SystemExit(err)
        image = image.convert_alpha()
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        return image


    loop = load_image("loop.png")
    left_arrow = load_image("left.png")
    right_arrow = load_image("right.png")
    error = load_image("error.png")
    cross = load_image("cross.png")
    cross = pygame.transform.scale(cross, (50, 50))

    app = Maps()
    app.main()
