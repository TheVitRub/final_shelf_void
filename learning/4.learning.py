from ultralytics import YOLO

def main():
    # Загрузка предобученной модели
    model = YOLO('my_best-shelf-void-model2026-01-29-10-38.pt')

    # Обучение
    results = model.train(
        data='dataset/2026-01-30_v1/data.yaml',
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,      # Теперь точно указываем видеокарту!
        workers=0,     # Количество потоков для загрузки данных
        name='yolo26_void_shelf',
        patience=50,
        save=True,
        plots=True,
        cache=True,
        amp=True,
        augment=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
    )

    model.save("my_best-shelf-void-model2026-01-30-09-06_v1.pt")

if __name__ == '__main__':
    main()