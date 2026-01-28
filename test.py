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

import threading
import time
from ultralytics.models import YOLO

from MVP.camera.camera import Camera
from MVP.show_picture.show_picture import ShowPicture

model_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\final_void_shelf\MVP\my_best-shelf-void-model2026-01-27-16-53.pt'
model = YOLO(model_path)
json_path=r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\shot_20260123_193334_shelf_coordinates.json'
camera1 = Camera(ip_camera='10.142.13.204')
camera2 = Camera(ip_camera='10.142.13.201')

camera_config = [
    '10.142.13.204',
    '10.142.13.197',
    '10.142.13.201',
    '10.142.13.195'
]

threads = []
test = ShowPicture(
    model=model)
test.start(json_path=json_path,
    camera=camera1)
quit()
for camera_ip in camera_config:
    camera = Camera(ip_camera=camera_ip)
    t = threading.Thread(
        target=test.run_periodic,
        args=(camera,),  # интервал 5 минут
        daemon=True  # чтобы потоки закрылись при нажатии Ctrl+C
    )
    threads.append(t)
    t.start()


try:
        # Держим основной поток живым, пока работают дочерние
        while True:
            time.sleep(1)
except KeyboardInterrupt:
        print("\nОстановка всех процессов...")

test.start()
#test.run_periodic()
#test.run_periodic(camera=camera2)