"""
Скрипт для подготовки датасета к обучению YOLO26
Проверяет и исправляет структуру датасета
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

def check_dataset_structure():
    """Проверяет структуру датасета и выявляет проблемы"""
    print("=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ ДАТАСЕТА")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.absolute()
    print(base_dir)
    images_dir = base_dir / "data" / "images" / "train"
    labels_dir = base_dir / "dataset" / "labels" / "train"
    print(images_dir)
    print(labels_dir)
    
    # Проверка изображений
    image_files = set(f.stem for f in images_dir.glob("*.jpg"))
    print(f"\n✓ Найдено изображений: {len(image_files)}")
    
    # Проверка аннотаций
    label_files = set(f.stem for f in labels_dir.glob("*.txt"))
    print(f"✓ Найдено аннотаций: {len(label_files)}")
    
    # Изображения без аннотаций
    images_without_labels = image_files - label_files
    if images_without_labels:
        print(f"\n⚠ Изображения без аннотаций ({len(images_without_labels)}):")
        for img in sorted(images_without_labels):
            print(f"  - {img}.jpg")
    
    # Аннотации без изображений
    labels_without_images = label_files - image_files
    if labels_without_images:
        print(f"\n⚠ Аннотации без изображений ({len(labels_without_images)}):")
        for lbl in sorted(labels_without_images):
            print(f"  - {lbl}.txt")
    
    # Проверка train.txt
    train_txt = base_dir / "dataset" / "train.txt"
    if train_txt.exists():
        with open(train_txt, 'r', encoding='utf-8') as f:
            train_paths = [line.strip() for line in f if line.strip()]
        print(f"\n✓ Записей в train.txt: {len(train_paths)}")
        
        # Проверка корректности путей
        incorrect_paths = []
        for path in train_paths:
            if not path.startswith("data/images/train/"):
                incorrect_paths.append(path)
        
        if incorrect_paths:
            print(f"⚠ Неправильные пути в train.txt: {len(incorrect_paths)}")
    
    return {
        'images': image_files,
        'labels': label_files,
        'images_without_labels': images_without_labels,
        'labels_without_images': labels_without_images
    }


def create_yolo_structure():
    """Создает правильную структуру для YOLO"""
    print("\n" + "=" * 60)
    print("СОЗДАНИЕ СТРУКТУРЫ YOLO")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.absolute()
    dataset_dir = base_dir / "dataset"
    images_dir = base_dir / "data" / "images" / "train"
    
    # Создаем структуру папок
    (dataset_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    print("✓ Создана структура папок")
    
    # Получаем список изображений с аннотациями
    label_files = {f.stem for f in (dataset_dir / "labels" / "train").glob("*.txt")}
    image_files = {f.stem for f in images_dir.glob("*.jpg")}
    valid_images = label_files & image_files
    
    print(f"✓ Найдено валидных пар (изображение + аннотация): {len(valid_images)}")
    
    # Разделяем на train и val (80/20)
    valid_images_list = sorted(valid_images)
    split_idx = int(len(valid_images_list) * 0.8)
    train_images = valid_images_list[:split_idx]
    val_images = valid_images_list[split_idx:]
    
    print(f"  - Train: {len(train_images)}")
    print(f"  - Val: {len(val_images)}")
    
    # Копируем изображения
    print("\nКопирование изображений...")
    for img_name in train_images:
        src = images_dir / f"{img_name}.jpg"
        dst = dataset_dir / "images" / "train" / f"{img_name}.jpg"
        shutil.copy2(src, dst)
    
    for img_name in val_images:
        src = images_dir / f"{img_name}.jpg"
        dst = dataset_dir / "images" / "val" / f"{img_name}.jpg"
        shutil.copy2(src, dst)
    
    print("✓ Изображения скопированы")
    
    # Перемещаем аннотации для val
    print("\nПеремещение аннотаций для валидации...")
    for img_name in val_images:
        src = dataset_dir / "labels" / "train" / f"{img_name}.txt"
        dst = dataset_dir / "labels" / "val" / f"{img_name}.txt"
        if src.exists():
            shutil.copy2(src, dst)
    
    print("✓ Аннотации для валидации скопированы")
    
    # Создаем train.txt и val.txt
    print("\nСоздание train.txt и val.txt...")
    train_txt_path = dataset_dir / "train.txt"
    val_txt_path = dataset_dir / "val.txt"
    
    with open(train_txt_path, 'w', encoding='utf-8') as f:
        for img_name in train_images:
            # Относительный путь от dataset директории
            f.write(f"images/train/{img_name}.jpg\n")
    
    with open(val_txt_path, 'w', encoding='utf-8') as f:
        for img_name in val_images:
            f.write(f"images/val/{img_name}.jpg\n")
    
    print("✓ Файлы train.txt и val.txt созданы")
    
    # Обновляем data.yaml
    print("\nОбновление data.yaml...")
    yaml_content = """names:
  0: "Пустое место в полке"
  1: "Немного пустое место"
path: dataset
train: train.txt
val: val.txt
nc: 2
"""
    with open(dataset_dir / "data.yaml", 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print("✓ data.yaml обновлен")
    
    return len(train_images), len(val_images)


if __name__ == "__main__":
    # Проверка текущей структуры
    stats = check_dataset_structure()
    
    # Создание правильной структуры
    if stats['images'] and stats['labels']:
        print("\n" + "=" * 60)
        response = input("Создать правильную структуру YOLO? (y/n): ")
        if response.lower() == 'y':
            train_count, val_count = create_yolo_structure()
            print("\n" + "=" * 60)
            print("✓ ДАТАСЕТ ПОДГОТОВЛЕН!")
            print("=" * 60)
            print(f"\nСтатистика:")
            print(f"  - Train изображений: {train_count}")
            print(f"  - Val изображений: {val_count}")
            print(f"\nСледующие шаги:")
            print("  1. Проверьте dataset/data.yaml")
            print("  2. Запустите обучение YOLO26")
        else:
            print("Операция отменена")
    else:
        print("\n⚠ Ошибка: недостаточно данных для создания датасета")

