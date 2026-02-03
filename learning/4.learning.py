from ultralytics import YOLO

def main():
    # Загрузка предобученной модели
    model = YOLO('yolo26n.pt')

    # Обучение
    results = model.train(
        data='dataset/final/data.yaml',

        epochs=100,
        imgsz=1280,
        batch=2,
        device=0,      # Теперь точно указываем видеокарту!
        workers=0,     # Количество потоков для загрузки данных
        name='yolo26_void_shelf',
        patience=10,
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

    model.save("my_best-shelf-void-model2026-02-01-12-15_V3_Обучение на боковом стеллаже.pt")

if __name__ == '__main__':
    main()