import sys
import pygame
import requests
from PIL import Image
from io import BytesIO


def convert_bytes(bytes_stream):
    image = Image.open(BytesIO(bytes_stream)).convert("RGB")
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.frombuffer(data, size, mode)


print("Введите начальные координаты")

lon = input("Широта: ")
lon = "44.99142" if not lon.strip() else lon

lat = input("Долгота: ")
lat = "53.198705" if not lat.strip() else lat

z = input("Задайте масштабирование(число 0 <= z <= 17): ")
z = "14" if not z else z

api_server = "http://static-maps.yandex.ru/1.x/?"

pygame.init()
screen = pygame.display.set_mode((600, 450))
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_PAGEUP and int(z) < 17:
                z = str(int(z) + 1)
            elif event.key == pygame.K_PAGEDOWN and int(z) > 0:
                z = str(int(z) - 1)

            if event.key == pygame.K_LEFT and float(lon) > 1:
                lon = str(float(lon)-(18-int(z))**2*0.0005)
            elif event.key == pygame.K_RIGHT and float(lon) < 179:
                lon = str(float(lon)+(18-int(z))**2*0.0005)

            if event.key == pygame.K_DOWN and float(lat) > -89:
                lat = str(float(lat)-(18-int(z))**2*0.0005)
            elif event.key == pygame.K_UP and float(lat) < 89:
                lat = str(float(lat)+(18-int(z))**2*0.0005)

        params = {
            "l": "sat,skl",
            "ll": ",".join([lon, lat]),
            "z": z
        }

        try:
            response = requests.get(api_server, params=params)

            if not response:
                print("Ошибка выполнения запроса")
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

        map_image = convert_bytes(response.content)

        screen.blit(map_image, (0, 0))
        pygame.display.flip()

pygame.quit()
