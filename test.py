"""
Скрипт для тестирования системы мониторинга наполнения полок.

Этот скрипт демонстрирует использование системы мониторинга полок с использованием
YOLO модели для детекции пустых мест. Поддерживает работу с одной или несколькими
камерами через RTSP потоки.

Основные возможности:
- Подключение к IP-камерам через RTSP
- Обработка видеопотока в реальном времени
- Детекция пустых мест на полках с помощью обученной YOLO модели
- Визуализация результатов с bounding boxes и информацией о наполнении
- Поддержка многопоточности для работы с несколькими камерами одновременно

Использование:
    1. Убедитесь, что модель YOLO находится по указанному пути
    2. Укажите путь к JSON файлу с координатами полок
    3. Настройте IP адреса камер в списке camera_config
    4. Запустите скрипт: python test.py

Зависимости:
    - ultralytics (YOLO)
    - MVP.camera.camera (класс Camera)
    - MVP.show_picture.show_picture (класс ShowPicture)

Автор: [Ваше имя]
Дата: 2026-01-27
"""

import os
from ultralytics.models import YOLO

from MVP.area_calculation.calculations import load_shelf_coordinates_from_json
from MVP.camera.camera import Camera
from MVP.show_picture.show_picture import ShowPicture
from MVP.config import ID_STORE

model_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\final_void_shelf\learning\my_best-shelf-void-model2026-01-30-09-06.pt'
model = YOLO(model_path)
json_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\shot_20260123_193334_shelf_coordinates.json'
shelf_coordinates = load_shelf_coordinates_from_json(json_path)
camera1 = Camera('10.142.13.207')



threads = []
test = ShowPicture(
    model=model)


test.start(json_path=json_path,
    camera=camera1)



