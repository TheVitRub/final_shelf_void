"""
Главный скрипт для запуска системы мониторинга наполнения полок.

Этот модуль является основной точкой входа для системы мониторинга полок.
Он инициализирует все необходимые компоненты (камера, модель YOLO, калькулятор площади)
и запускает обработку видеопотока с визуализацией результатов.

Основные функции:
    - Подключение к камере через RTSP
    - Загрузка обученной YOLO модели
    - Загрузка координат полок из JSON файла
    - Обработка видеопотока в реальном времени
    - Визуализация результатов детекции (bounding boxes, процент наполнения)
    - Отображение обработанных кадров с информацией о наполнении полок

Использование:
    python MVP/main.py

Настройка:
    - Измените model_path на путь к вашей обученной модели
    - Укажите json_path к файлу с координатами полок
    - Настройте параметры в MVP/config.py (SKIP_FRAMES, MAX_DISPLAY_WIDTH)

Управление:
    - Нажмите 'q' или ESC для выхода из программы
    - Ctrl+C для остановки обработки

Автор: [Ваше имя]
Дата: 2026-01-27
"""

import cv2
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

# Функция обратного вызова для обработки результатов
def on_frame_processed(frame, results):
    print(f"Процент наполнения: {results['fill_percentage']:.2f}%")
    print(f"Обнаружено объектов: {results['num_objects']}")

def main():
    camera = Camera()
    
    # Обработка потока кадров
    try:
        model_path = r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\MVP\my_best-shelf-void-model.pt'
        model = YOLO(model_path)
        area = AreaCalculator(model)
        json_path = r'C:\Users\ryabovva.VOLKOVKMR\PycharmProjects\learn_void_shelf\shot_20260123_193334_shelf_coordinates.json'
        shelf_coordinates = load_shelf_coordinates_from_json(json_path)
        for frame, results in area.process_camera_stream(
                camera=camera,
                shelf_coordinates=shelf_coordinates,
                filter_objects_in_shelves=True,
                callback=on_frame_processed,
                skip_frames=SKIP_FRAMES
            ):
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

if __name__ == "__main__":
    main()