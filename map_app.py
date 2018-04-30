import os
import requests
from gui import *
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
        self.lon_lat = "45.016735,53.194065"
        self.z = "4"
        self.mode = "sat,skl"
        self.mark_ll = ""
        self.text = "Введите поисковый запрос"

    def set_params(self, ll=None, z=None, mark_ll=None, text=None):
        if ll is not None:
            self.lon_lat = ll
        if z is not None:
            self.z = z
        if mark_ll is not None:
            self.mark_ll = mark_ll
        if text is not None:
            self.text = text

    def get_params(self, mode="single",
                   ll=False, z=False, mark_ll=False, text=False, map_mode=False):
        if mode == "single":
            if ll:
                return self.lon_lat
            if z:
                return self.z
            if mark_ll:
                return self.mark_ll
            if text:
                return self.text
            if map_mode:
                return self.mode

        elif mode == "dict":
            result = {}
            if ll:
                result["ll"] = self.lon_lat
            if z:
                result["z"] = self.z
            if mark_ll:
                result["mark_ll"] = self.mark_ll
            if text:
                result["text"] = self.text
            if map_mode:
                result["map_mode"] = self.mode
            return result

    def set_text(self, text):
        if type(text) is str:
            self.text = text

    def change_map_mode(self, direction):
        modes = ["map", "sat", "sat,skl"]
        mode_index = modes.index(self.mode) + direction
        self.mode = modes[mode_index % len(modes)]

    def reset_params(self):
        self.mark_ll = ""
        self.text = "Введите поисковый запрос"

    def static_request(self):
        static_api_server = "https://static-maps.yandex.ru/1.x/"
        params = {
            "l": self.mode,
            "ll": self.lon_lat,
            "z": self.z
        }
        if self.mark_ll:
            params["pt"] = ",".join((self.mark_ll, "pm2vvm"))

        try:
            response = requests.get(static_api_server, params=params)
            if not response:
                return error
            return convert_bytes(response.content)

        except Exception as err:
            print(">>> Static error:", err)
            return error

    def geocoder_request(self, search_request):
        geocode_api_server = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "geocode": search_request,
            "format": "json"
        }

        try:

            response = requests.get(geocode_api_server, params=params)
            json_response = response.json()
            if not json_response["response"]["GeoObjectCollection"]["featureMember"]:
                self.text = "Ничего не найдено"
                return
            return json_response

        except Exception as err:
            print(">>> Geocoder error:", err)
            self.text = "Проверьте наличие сети Интернет"


def read_json_toponym(json_toponym, ll=False, text=False, postal_code=False):
    try:

        result = {}
        toponym_data = json_toponym["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

        if ll:
            result["ll"] = toponym_data["Point"]["pos"].replace(" ", ",")
        if text:
            result["text"] = toponym_data["metaDataProperty"]["GeocoderMetaData"]["text"]
        if postal_code:
            address = toponym_data["metaDataProperty"]["GeocoderMetaData"]["Address"]
            if "postal_code" in address:
                result["postal_code"] = address["postal_code"]
            else:
                result["postal_code"] = "Не определен"

        return result

    except IndexError or KeyError as err:
        print(">>> ReadingError :", err)


def main():
    bg_color = 45, 20, 15
    fg_color = 245, 250, 115
    press_left = False
    press_right = False

    app = Maps()
    clock = pygame.time.Clock()
    pygame.key.set_repeat(500, 200)

    gui = GUI()

    search_textbox = TextBox((35, 30, 754, 60), fg_color, bg_color)
    search_button = ImageButton((803, 25, 74, 74), fg_color, loop)
    status_bar = Label((35, 115, 754, 60), bg_color, "", fg_color)

    left_mode = ImageButton((645, 230, 34, 54), fg_color, left_arrow)
    right_mode = ImageButton((851, 230, 34, 54), fg_color, right_arrow)
    current_mode = Label((689, 230, 152, 54), fg_color, app.mode, bg_color)

    reset_button = ImageButton((803, 112, 74, 74), fg_color, cross)

    postal_code_mode = Label((645, 324, 174, 54), fg_color, "Индекс", bg_color)
    postal_code_checkbox = Checkbox((830, 324, 54, 54), fg_color, bg_color)
    cur_postal_code = Label((645, 388, 239, 60), fg_color, "", bg_color, hidden=True)

    gui.add_element(search_button)
    gui.add_element(left_mode)
    gui.add_element(right_mode)
    gui.add_element(current_mode)
    gui.add_element(search_textbox)
    gui.add_element(status_bar)
    gui.add_element(reset_button)
    gui.add_element(postal_code_mode)
    gui.add_element(postal_code_checkbox)
    gui.add_element(cur_postal_code)

    map_image = app.static_request()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key in \
               [pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_LEFT, pygame.K_RIGHT,
                    pygame.K_UP, pygame.K_DOWN] and not search_textbox.get_active():

                data = app.get_params(ll=True, z=True, mode="dict")
                lon, lat = map(lambda x: float(x), data["ll"].split(","))
                z = int(data["z"])

                shift = [30, 25, 20, 15, 8, 4, 2, 1, 0.5, 0.25, 0.1, 0.05, 0.025, 0.01, 0.005, 0.0025, 0.0001]

                if event.key == pygame.K_PAGEUP and z < 17:
                    z = z + 1
                elif event.key == pygame.K_PAGEDOWN and z > 2:
                    z = z - 1

                if event.key == pygame.K_LEFT and lon > 1:
                    lon = lon - shift[z - 1]
                elif event.key == pygame.K_RIGHT and lon < 179:
                    lon = lon + shift[z - 1]
                if event.key == pygame.K_DOWN and lat > -89:
                    lat = lat - shift[z - 1]
                elif event.key == pygame.K_UP and lat < 89:
                    lat = lat + shift[z - 1]

                app.set_params(ll=str(lon) + "," + str(lat), z=str(z))

                map_image = app.static_request()

            gui.get_event(event)

        gui.update()

        screen.fill(bg_color)
        # Отрисовка карты с рамкой
        screen.fill(fg_color, (10, 220, 620, 470))
        screen.blit(map_image, (20, 230))
        # Отрисовка итерфейса
        gui.render(screen)

        pygame.display.flip()
        clock.tick(60)

        if left_mode.get_pressed() and not press_left:
            app.change_map_mode(-1)
            map_image = app.static_request()
            current_mode.set_text(app.get_params(map_mode=True))
            press_left = not press_left
        elif not left_mode.get_pressed() and press_left:
            press_left = not press_left

        if right_mode.get_pressed() and not press_right:
            app.change_map_mode(1)
            map_image = app.static_request()
            current_mode.set_text(app.get_params(map_mode=True))
            press_right = not press_right
        elif not right_mode.get_pressed() and press_right:
            press_right = not press_right

        if search_button.get_pressed():
            search_textbox.set_done(True)

        elif reset_button.get_pressed():
            app.reset_params()
            status_bar.set_font_size()
            map_image = app.static_request()

        if search_textbox.get_done() and search_textbox.get_text():
            request = app.geocoder_request(search_textbox.get_text())
            if request:
                data = read_json_toponym(request,
                                         ll=True, text=True, postal_code=True)
                cur_postal_code.set_text(data["postal_code"])
                status_bar.set_font_size()
                app.set_params(ll=data["ll"], mark_ll=data["ll"], text=data["text"])
                map_image = app.static_request()

        cur_postal_code.set_hidden(not postal_code_checkbox.get_pressed())
        status_bar.set_text(app.get_params(text=True))

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

    main()
