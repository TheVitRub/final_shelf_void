"""
Скрипт для исправления файлов train.txt и val.txt в датасете YOLO.

Этот скрипт проверяет существование изображений и аннотаций в датасете,
удаляет несуществующие записи из train.txt и val.txt, и создает новые
файлы только с валидными путями. Также автоматически разделяет данные
на train/val в соотношении 80/20, если валидационный набор пуст.

Основные функции:
    - Проверка существования изображений и аннотаций
    - Фильтрация несуществующих файлов из train.txt и val.txt
    - Автоматическое разделение на train/val (80/20) при необходимости
    - Создание относительных путей для YOLO
    - Вывод статистики по датасету

Структура датасета:
    learning/dataset/
    ├── images/
    │   ├── train/
    │   └── val/
    ├── labels/
    │   ├── train/
    │   └── val/
    ├── train.txt
    ├── val.txt
    └── data.yaml

Использование:
    python learning/2.fix_train_txt.py

Результат:
    - Обновленные файлы train.txt и val.txt с валидными путями
    - Автоматическое создание val набора при необходимости
    - Статистика по количеству файлов в каждом наборе

Примечание:
    Скрипт использует относительные пути от директории dataset/,
    что является стандартным форматом для YOLO.

Автор: [Ваше имя]
Дата: 2026-01-27
"""

from pathlib import Path

def fix_train_val_files():
    dataset_dir = Path("learning/dataset").absolute()
    
    # Получаем все существующие изображения
    train_images_dir = dataset_dir / "images" / "train"
    val_images_dir = dataset_dir / "images" / "val"
    
    train_images = {f.stem for f in train_images_dir.glob("*.jpg")}
    val_images = {f.stem for f in val_images_dir.glob("*.jpg")} if val_images_dir.exists() else set()
    
    # Получаем все существующие аннотации
    train_labels_dir = dataset_dir / "labels" / "train"
    val_labels_dir = dataset_dir / "labels" / "val"
    
    train_labels = {f.stem for f in train_labels_dir.glob("*.txt")}
    val_labels = {f.stem for f in val_labels_dir.glob("*.txt")} if val_labels_dir.exists() else set()
    
    # Находим валидные пары (изображение + аннотация)
    valid_train = sorted(train_images & train_labels)
    valid_val = sorted(val_images & val_labels)
    
    print(f"Найдено train изображений: {len(train_images)}")
    print(f"Найдено train аннотаций: {len(train_labels)}")
    print(f"Валидных train пар: {len(valid_train)}")
    print(f"\nНайдено val изображений: {len(val_images)}")
    print(f"Найдено val аннотаций: {len(val_labels)}")
    print(f"Валидных val пар: {len(valid_val)}")
    
    # Если val пустой, разделяем train на train/val (80/20)
    if len(valid_val) == 0 and len(valid_train) > 0:
        print("\nРазделяем train на train/val (80/20)...")
        split_idx = int(len(valid_train) * 0.8)
        valid_val = valid_train[split_idx:]
        valid_train = valid_train[:split_idx]
        
        # Создаем папки для val
        (dataset_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
        (dataset_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
        
        # Копируем изображения и аннотации для val
        import shutil
        for img_name in valid_val:
            # Копируем изображение
            src_img = train_images_dir / f"{img_name}.jpg"
            dst_img = val_images_dir / f"{img_name}.jpg"
            if src_img.exists() and not dst_img.exists():
                shutil.copy2(src_img, dst_img)
            
            # Копируем аннотацию
            src_label = train_labels_dir / f"{img_name}.txt"
            dst_label = val_labels_dir / f"{img_name}.txt"
            if src_label.exists() and not dst_label.exists():
                shutil.copy2(src_label, dst_label)
        
        print(f"Создано val: {len(valid_val)} изображений")
    
    # Создаем train.txt с относительными путями
    train_txt_path = dataset_dir / "train.txt"
    with open(train_txt_path, 'w', encoding='utf-8') as f:
        for img_name in valid_train:
            # Относительный путь от dataset директории
            f.write(f"images/train/{img_name}.jpg\n")
    
    print(f"\n[OK] Создан train.txt с {len(valid_train)} путями")
    
    # Создаем val.txt с относительными путями
    val_txt_path = dataset_dir / "val.txt"
    with open(val_txt_path, 'w', encoding='utf-8') as f:
        for img_name in valid_val:
            # Относительный путь от dataset директории
            f.write(f"images/val/{img_name}.jpg\n")
    
    print(f"[OK] Создан val.txt с {len(valid_val)} путями")
    
    # Показываем примеры путей
    if valid_train:
        print(f"\nПримеры путей в train.txt:")
        for i, img_name in enumerate(valid_train[:3]):
            print(f"  {i+1}. images/train/{img_name}.jpg")
        if len(valid_train) > 3:
            print(f"  ... и еще {len(valid_train) - 3} файлов")
    
    if valid_val:
        print(f"\nПримеры путей в val.txt:")
        for i, img_name in enumerate(valid_val[:3]):
            print(f"  {i+1}. images/val/{img_name}.jpg")
        if len(valid_val) > 3:
            print(f"  ... и еще {len(valid_val) - 3} файлов")
    
    # Показываем файлы без аннотаций
    train_without_labels = train_images - train_labels
    if train_without_labels:
        print(f"\n⚠ Изображения train без аннотаций ({len(train_without_labels)}):")
        for img_name in sorted(train_without_labels)[:5]:
            print(f"  - {img_name}.jpg")
        if len(train_without_labels) > 5:
            print(f"  ... и еще {len(train_without_labels) - 5} файлов")
    
    return len(valid_train), len(valid_val)


if __name__ == "__main__":
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ train.txt и val.txt")
    print("=" * 60)
    train_count, val_count = fix_train_val_files()
    print("\n" + "=" * 60)
    print(f"[OK] ГОТОВО! Train: {train_count}, Val: {val_count}")
    print("=" * 60)
    print("\nТеперь можно запускать обучение!")

