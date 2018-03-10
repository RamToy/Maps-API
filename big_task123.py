import pygame
import requests
import os
import sys

# Координты центра области, которую отображаем
coords = ",".join(input("Введите координаты отображения карты(2 вещественных числа через пробел в порядке 'широта_долгота'): ").split())
# Масштабирование карты
z = input("Задайте масштабирование(число 0 <= z <= 17): ")

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        coords = coords.split(",")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP and int(z) < 17:
            z = str(int(z)+1)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN and int(z) > 0:
            z = str(int(z)-1)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and float(coords[0]) > 1:
            coords[1] = str(float(coords[1])-(18-int(z))**2*0.0005)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and float(coords[0]) < 179:
            coords[1] = str(float(coords[1])+(18-int(z))**2*0.0005)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and float(coords[1]) > -89:
            coords[0] = str(float(coords[0])-(18-int(z))**2*0.0005)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and float(coords[1]) < 89:
            coords[0] = str(float(coords[0])+(18-int(z))**2*0.0005)
        coords = ",".join(coords)
        map_request = "http://static-maps.yandex.ru/1.x/?ll={}&z={}&size=600,450&l=sat,skl".format(coords, z)
        response = None

        try:
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

        map_file = "map.png"

        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)
        # Рисуем картинку, загружаемую из только что созданного файла.
        screen.blit(pygame.image.load(map_file), (0, 0))
        # Переключаем экран и ждем закрытия окна.
        pygame.display.flip()
pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)