"""
Скрипт для исправления путей в train.txt и val.txt на абсолютные.

Этот скрипт преобразует относительные пути в train.txt и val.txt в абсолютные,
что необходимо для корректной работы YOLO при обучении. Также обновляет
файл data.yaml с абсолютным путем к датасету.

Основные функции:
    - Преобразование относительных путей в абсолютные
    - Проверка существования файлов перед добавлением в список
    - Обновление data.yaml с абсолютным путем к датасету
    - Вывод предупреждений о несуществующих файлах

Структура датасета:
    learning/dataset/
    ├── images/
    │   ├── train/
    │   └── val/
    ├── labels/
    │   ├── train/
    │   └── val/
    ├── train.txt (с абсолютными путями)
    ├── val.txt (с абсолютными путями)
    └── data.yaml (с абсолютным путем)

Использование:
    python learning/3.fix_dataset_paths.py

Результат:
    - train.txt и val.txt с абсолютными путями к изображениям
    - Обновленный data.yaml с абсолютным путем к датасету
    - Статистика по количеству обработанных файлов

Примечание:
    Этот скрипт должен запускаться после 2.fix_train_txt.py.
    Абсолютные пути необходимы для некоторых конфигураций YOLO.

Автор: [Ваше имя]
Дата: 2026-01-27
"""

from pathlib import Path
import os

def fix_paths():
    """Исправляет пути в train.txt и val.txt на абсолютные"""
    base_dir = Path(__file__).parent.absolute()
    print(base_dir)
    dataset_dir = base_dir / "dataset" / "final"
    
    # Читаем train.txt и исправляем пути
    train_txt_path = dataset_dir / "train.txt"
    if train_txt_path.exists():
        with open(train_txt_path, 'r', encoding='utf-8') as f:
            train_lines = [line.strip() for line in f if line.strip()]
        
        # Проверяем существование файлов и создаем абсолютные пути
        valid_train_paths = []
        for line in train_lines:
            # Путь относительно dataset директории
            rel_path = Path(line)
            abs_path = dataset_dir / rel_path
            
            if abs_path.exists():
                # Используем абсолютный путь
                valid_train_paths.append(str(abs_path))
            else:
                print(f"[WARNING] Файл не найден: {abs_path}")
        
        # Записываем обратно с абсолютными путями
        with open(train_txt_path, 'w', encoding='utf-8') as f:
            for path in valid_train_paths:
                f.write(f"{path}\n")
        
        print(f"[OK] Исправлено {len(valid_train_paths)} путей в train.txt")
    
    # Читаем val.txt и исправляем пути
    val_txt_path = dataset_dir / "val.txt"
    if val_txt_path.exists():
        with open(val_txt_path, 'r', encoding='utf-8') as f:
            val_lines = [line.strip() for line in f if line.strip()]
        
        # Проверяем существование файлов и создаем абсолютные пути
        valid_val_paths = []
        for line in val_lines:
            # Путь относительно dataset директории
            rel_path = Path(line)
            abs_path = dataset_dir / rel_path
            
            if abs_path.exists():
                # Используем абсолютный путь
                valid_val_paths.append(str(abs_path))
            else:
                print(f"[WARNING] Файл не найден: {abs_path}")
        
        # Записываем обратно с абсолютными путями
        with open(val_txt_path, 'w', encoding='utf-8') as f:
            for path in valid_val_paths:
                f.write(f"{path}\n")
        
        print(f"[OK] Исправлено {len(valid_val_paths)} путей в val.txt")
    
    # Обновляем data.yaml - используем абсолютный путь
    yaml_path = dataset_dir / "data.yaml"
    if yaml_path.exists():
        yaml_content = f"""names:
  0: "Пустое место в полке"
  1: "Немного пустое место"
path: {str(dataset_dir).replace(chr(92), '/')}
train: train.txt
val: val.txt
nc: 2
"""
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        print(f"[OK] Обновлен data.yaml с абсолютным путем: {dataset_dir}")
    
    return len(valid_train_paths), len(valid_val_paths)


if __name__ == "__main__":
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ ПУТЕЙ В ДАТАСЕТЕ")
    print("=" * 60)
    train_count, val_count = fix_paths()
    print("\n" + "=" * 60)
    print(f"[OK] ГОТОВО! Train: {train_count}, Val: {val_count}")
    print("=" * 60)

