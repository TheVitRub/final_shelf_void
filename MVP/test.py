"""
Простой тестовый скрипт для проверки работы системы мониторинга полок.

Этот скрипт предназначен для быстрого тестирования функциональности
детекции пустых мест на полках. Запускает периодический мониторинг
с заданным интервалом.

Использование:
    1. Укажите путь к модели YOLO в model_path
    2. Укажите путь к JSON файлу с координатами полок в json_path
    3. Запустите: python MVP/test.py

Примечание:
    Скрипт использует относительные импорты, поэтому должен запускаться
    из корневой директории проекта.

Автор: [Ваше имя]
Дата: 2026-01-27
"""

from show_picture.show_picture import ShowPicture

model_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\final_void_shelf\MVP\my_best-shelf-void-model2026-01-27-16-53.pt'
json_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\shot_20260123_193334_shelf_coordinates.json'
test = ShowPicture(model_path, json_path)
test.run_periodic()
