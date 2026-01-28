"""
Модуль для визуализации и отображения результатов детекции пустых мест на полках.

Этот модуль предоставляет класс ShowPicture для отображения результатов работы
системы мониторинга полок. Поддерживает как непрерывный видеопоток, так и
периодический мониторинг с заданным интервалом.

Основные возможности:
    - Отображение видеопотока с камеры в реальном времени
    - Визуализация bounding boxes обнаруженных объектов
    - Отображение информации о проценте наполнения полок
    - Поддержка масштабирования кадров для удобного просмотра
    - Периодический вывод статистики (по умолчанию каждые 5 минут)
    - Обработка одного кадра для периодического мониторинга

Классы:
    ShowPicture: Основной класс для визуализации результатов детекции

Методы ShowPicture:
    - start(): Запускает непрерывную обработку видеопотока с отображением
    - frame(): Обрабатывает один кадр и выводит результаты раз в 5 минут
    - run_periodic(): Запускает периодический мониторинг с заданным интервалом

Использование:
    from MVP.show_picture.show_picture import ShowPicture
    from MVP.camera.camera import Camera
    from ultralytics import YOLO
    
    model = YOLO('path/to/model.pt')
    camera = Camera(ip_camera='192.168.1.100')
    show = ShowPicture(model=model)
    show.start(camera=camera, json_path='shelf_coordinates.json')

Автор: [Ваше имя]
Дата: 2026-01-27
"""

import cv2
import time
from ultralytics import YOLO

from MVP.area_calculation.area_calculation import AreaCalculator
from MVP.area_calculation.calculations import load_shelf_coordinates_from_json
from MVP.camera.camera import Camera
from MVP.config import SKIP_FRAMES, MAX_DISPLAY_WIDTH


def resize_frame(frame, max_width=MAX_DISPLAY_WIDTH):
    """
    Масштабирует кадр, сохраняя пропорции, чтобы ширина не превышала max_width.

    Args:
        frame: Входной кадр (numpy array)
        max_width: Максимальная ширина для отображения

    Returns:
        Tuple: (масштабированный кадр, коэффициент масштабирования)
    """
    height, width = frame.shape[:2]

    if width <= max_width:
        return frame, 1.0

    # Вычисляем коэффициент масштабирования
    scale = max_width / width
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Масштабируем кадр
    resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    return resized_frame, scale


def on_frame_processed(frame, results):
    print(f"Процент наполнения: {results['fill_percentage']:.2f}%")
    print(f"Обнаружено объектов: {results['num_objects']}")


class ShowPicture:
    def __init__(self, model:YOLO):

        self.area = AreaCalculator(model)
        self.last_output_time = 0
        self.output_interval = 300  # 5 минут в секундах
    def start(self, camera:Camera, json_path:str, video:bool = True):

        try:
            shelf_coordinates = load_shelf_coordinates_from_json(json_path)
            for frame, results in self.area.process_camera_stream(
                camera=camera,
                shelf_coordinates=shelf_coordinates,
                filter_objects_in_shelves=True,
                callback=on_frame_processed,
                skip_frames=SKIP_FRAMES
            ):
                if video:
                    # Сначала масштабируем кадр для отображения
                    display_frame, scale = resize_frame(frame.copy(), MAX_DISPLAY_WIDTH)

                    # Рисуем bounding boxes для всех обнаруженных объектов
                    # Координаты объектов масштабируются тем же коэффициентом, что и кадр
                    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
                    for obj in results['objects_info']:
                        x1, y1, x2, y2 = obj['coordinates']
                        # Масштабируем координаты под масштабированный кадр
                        x1, y1, x2, y2 = int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale)

                        # Выбираем цвет в зависимости от класса
                        color = colors[obj['class_id'] % len(colors)]

                        # Рисуем прямоугольник (bounding box) с масштабированной толщиной
                        box_thickness = max(1, int(2 * scale)) if scale < 1.0 else 2
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, box_thickness)

                        # Формируем текст с классом и уверенностью
                        label = f"{obj['class']} {obj['confidence']:.2f}"

                        # Вычисляем размер текста для фона (масштабируем размер шрифта)
                        font_scale = 0.6 * scale if scale < 1.0 else 0.6
                        thickness = max(1, int(2 * scale)) if scale < 1.0 else 2
                        (text_width, text_height), baseline = cv2.getTextSize(
                            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
                        )

                        # Рисуем фон для текста
                        cv2.rectangle(
                            display_frame,
                            (x1, y1 - text_height - baseline - 5),
                            (x1 + text_width, y1),
                            color,
                            -1
                        )

                        # Рисуем текст
                        cv2.putText(
                            display_frame,
                            label,
                            (x1, y1 - baseline - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale,
                            (255, 255, 255),
                            thickness
                        )

                    # Добавляем текст с информацией о проценте наполнения
                    fill_text = f"Fill: {results['fill_percentage']:.1f}%"
                    objects_text = f"Objects: {results['num_objects']}"

                    # Масштабируем размеры информационной панели
                    info_font_scale = 1.0 * scale if scale < 1.0 else 1.0
                    info_thickness = max(1, int(2 * scale)) if scale < 1.0 else 2
                    info_panel_x2 = int(300 * scale) if scale < 1.0 else 300
                    info_panel_y2 = int(85 * scale) if scale < 1.0 else 85

                    # Рисуем фон для информационного текста
                    cv2.rectangle(display_frame, (5, 5), (info_panel_x2, info_panel_y2), (0, 0, 0), -1)
                    cv2.rectangle(display_frame, (5, 5), (info_panel_x2, info_panel_y2), (0, 255, 0), info_thickness)

                    # Рисуем текст на кадре
                    text_y1 = int(35 * scale) if scale < 1.0 else 35
                    text_y2 = int(75 * scale) if scale < 1.0 else 75
                    cv2.putText(display_frame, fill_text, (10, text_y1),
                                cv2.FONT_HERSHEY_SIMPLEX, info_font_scale, (0, 255, 0), info_thickness)
                    cv2.putText(display_frame, objects_text, (10, text_y2),
                                cv2.FONT_HERSHEY_SIMPLEX, info_font_scale, (0, 255, 0), info_thickness)

                    # Отображаем кадр (уже масштабированный)
                    cv2.imshow('Shelf Monitoring', display_frame)

                    # Выход по нажатию 'q' или ESC
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' или ESC
                        break

        except KeyboardInterrupt:
            print("Остановка обработки потока...")

        finally:
            camera.release()
            cv2.destroyAllWindows()


    def frame(self, camera:Camera, shelf_coordinates):
        """
        Получает один кадр с камеры, обрабатывает его и выводит результаты раз в 5 минут.
        
        Returns:
            Tuple (frame, results_dict) или None, если еще не прошло 5 минут с последнего вывода
        """

        # Получаем один кадр и обрабатываем его
        frame, results = self.area.frame_camera(
            camera=camera,
            shelf_coordinates=shelf_coordinates,
            filter_objects_in_shelves=True
        )
        
        # Проверяем, прошло ли 5 минут с последнего вывода
        current_time = time.time()
        if current_time - self.last_output_time >= self.output_interval:
            # Выводим результаты
            print("\n" + "=" * 60)
            print(f"РЕЗУЛЬТАТЫ АНАЛИЗА (время: {time.strftime('%Y-%m-%d %H:%M:%S')})")
            print("=" * 60)
            print(f"Размер изображения: {results['image_size'][0]}x{results['image_size'][1]}")
            print(f"Обнаружено объектов: {results['num_objects']}")
            print(f"Общая площадь объектов: {results['total_objects_area']:.2f} пикселей²")
            print(f"Общая площадь полок: {results['shelf_total_area']:.2f} пикселей²")
            print(f"Процент наполнения: {results['fill_percentage']:.2f}%")
            print("\n" + "-" * 60)
            print("Детали объектов:")
            print("-" * 60)
            
            for obj in results['objects_info']:
                print(f"Объект {obj['id']}:")
                print(f"  Класс: {obj['class']} (ID: {obj['class_id']})")
                print(f"  Уверенность: {obj['confidence']:.2%}")
                print(f"  Координаты: ({obj['coordinates'][0]:.0f}, {obj['coordinates'][1]:.0f}) -> "
                      f"({obj['coordinates'][2]:.0f}, {obj['coordinates'][3]:.0f})")
                print(f"  Площадь: {obj['area']:.2f} пикселей²")
                print()
            
            # Обновляем время последнего вывода
            self.last_output_time = current_time
            return frame, results
        else:
            return None
    
    def run_periodic(self, camera:Camera, shelf_coordinates):
        """
        Запускает цикл, который получает данные с камеры и выводит их раз в 5 минут.
        Камера подключается один раз при инициализации класса.
        """
        print("Запуск периодического мониторинга...")
        print(f"Данные будут получаться и выводиться каждые {self.output_interval // 60} минут")
        print("Для остановки нажмите Ctrl+C\n")
        
        # Первый вывод сразу
        self.last_output_time = 0

        try:
            while True:
                # Получаем данные с камеры и выводим, если прошло 5 минут
                result = self.frame(camera=camera, shelf_coordinates=shelf_coordinates)
                
                if result is None:
                    # Еще не прошло 5 минут, ждем перед следующей проверкой
                    time.sleep(10)  # Проверяем каждые 10 секунд
                else:
                    # Данные были выведены, ждем 5 минут перед следующим получением
                    time.sleep(self.output_interval)
                
        except KeyboardInterrupt:
            print("\nОстановка мониторинга...")
        finally:
            camera.release()
            print("Камера отключена")