import os
import sys
import requests
import pprint
from Projects.Maps_API.GUI import *
from PIL import Image
from io import BytesIO


def convert_bytes(bytes_stream):
    image = Image.open(BytesIO(bytes_stream)).convert("RGB")
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.frombuffer(data, size, mode)


class Maps:
    def __init__(self):
        self.lon = "44.99142"
        self.lat = "53.198705"
        self.mode = "sat,skl"
        self.z = "4"
        self.bg_color = 83, 29, 18
        self.fg_color = 233, 230, 0
        self.map_image = None
        self.press1 = False
        self.press2 = False
        self.search_request = ""

    def new_static_request(self):
        static_api_server = "http://static-maps.yandex.ru/1.x/"
        params = {
            "l": self.mode,
            "ll": ",".join([self.lon, self.lat]),
            "z": self.z
        }
        try:
            response = requests.get(static_api_server, params=params)
            if not response:
                print("Ошибка выполнения запроса")
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
            return convert_bytes(response.content)
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

    def new_geocoder_request(self):
        geocode_api_server = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "geocode": self.search_request,
            "format": "json"
        }
        try:
            response = requests.get(geocode_api_server, params=params)
            if not response:
                print("Ошибка выполнения запроса:")
                print(self.search_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
            json_response = response.json()
            self.lon, self.lat = json_response["response"]["GeoObjectCollection"]["featureMember"][0]\
                                              ["GeoObject"]["Point"]["pos"].split()
        except IndexError:
            print("Результатов не найдено")
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

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
        running = True

        gui = GUI()

        search_button = ImageButton((753, 23, 74, 74), self.fg_color, loop, True)
        left_mode = ImageButton((640, 170, 34, 54), self.fg_color, left_arrow, True)
        right_mode = ImageButton((846, 170, 34, 54), self.fg_color, right_arrow, True)
        current_mode = Label((685, 170, 152, 54), self.fg_color, self.mode, self.bg_color, True)
        search_textbox = TextBox((75, 33, 650, 54), -1, "", (200, 200, 0))

        gui.add_element(search_button)
        gui.add_element(left_mode)
        gui.add_element(right_mode)
        gui.add_element(current_mode)
        gui.add_element(search_textbox)

        self.map_image = self.new_static_request()

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

                    shift = round((18 - int(self.z)) * (0.0001 * (18 - int(self.z))), 4)
                    if event.key == pygame.K_LEFT and float(self.lon) > 1:
                        self.lon = str(float(self.lon) - shift)
                    elif event.key == pygame.K_RIGHT and float(self.lon) < 179:
                        self.lon = str(float(self.lon) + shift)

                    if event.key == pygame.K_DOWN and float(self.lat) > -89:
                        self.lat = str(float(self.lat) - shift)
                    elif event.key == pygame.K_UP and float(self.lat) < 89:
                        self.lat = str(float(self.lat) + shift)

                    self.map_image = self.new_static_request()

                gui.get_event(event)

            if left_mode.pressed and not self.press1:
                self.change_mode(-1)
                self.map_image = self.new_static_request()
                current_mode.text = self.mode
                self.press1 = True
            elif not left_mode.pressed and self.press1:
                self.press1 = False
            if right_mode.pressed and not self.press2:
                self.change_mode(1)
                self.map_image = self.new_static_request()
                current_mode.text = self.mode
                self.press2 = True
            elif not right_mode.pressed and self.press2:
                self.press2 = False

            if search_button.pressed:
                search_textbox.done = True

            if search_textbox.done and search_textbox.text:
                self.search_request = search_textbox.text
                self.new_geocoder_request()
                self.map_image = self.new_static_request()

            gui.update()
            screen.fill(self.bg_color)
            screen.blit(self.map_image, (20, 130))
            screen.blit(search_line, (70, 20))
            gui.render(screen)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))

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


    search_line = load_image("search_line.png")
    loop = load_image("loop.png")
    left_arrow = load_image("left.png")
    right_arrow = load_image("right.png")

    app = Maps()
    app.main()
