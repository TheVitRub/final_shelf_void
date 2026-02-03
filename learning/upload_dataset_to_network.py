"""
Скрипт для загрузки датасета на сетевой диск.
Удаляет всё из T:\\Рябов\\learning\\dataset\\ и загружает новую папку.
"""

import sys
import shutil
from pathlib import Path

# Настройки путей
LOCAL_DATASET_PATH = "learning/dataset/final" # <--- МЕНЯТЬ ПАПКУ ТУТ

# Конфигурация сетевого диска
NETWORK_BASE_PATH = Path(r"T:\Рябов\learning")
NETWORK_DATASET_PATH = NETWORK_BASE_PATH / "dataset"

def delete_folder_contents(folder_path: Path):
    """Удаляет все содержимое указанной папки."""
    print(f"Удаление содержимого: {folder_path}")
    
    if not folder_path.exists():
        print("Папка не существует, удалять нечего.")
        return

    count = 0
    for item in folder_path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                count += 1
        except Exception as e:
            print(f"  Ошибка при удалении {item}: {e}")
            
    print(f"Удалено {count} объектов из {folder_path}")


def upload_folder(local_folder: Path, destination_folder: Path):
    """Копирует локальную папку в место назначения."""
    print(f"\nКопирование папки: {local_folder}")
    print(f"Назначение: {destination_folder}")
    
    if not local_folder.exists():
        print(f"ОШИБКА: Локальная папка {local_folder} не существует!")
        return False
    
    try:
        # Создаем родительскую директорию если её нет
        destination_folder.parent.mkdir(parents=True, exist_ok=True)
        
        # Копируем дерево директорий
        shutil.copytree(local_folder, destination_folder)
        
        # Подсчитаем файлы для вывода
        files_count = sum(1 for _ in destination_folder.rglob("*") if _.is_file())
        print(f"\nВсего скопировано: {files_count} файлов")
        return True
    except Exception as e:
        print(f"    ОШИБКА при копировании: {e}")
        return False


def main():
    # Определяем абсолютный путь локальной папки
    local_folder = Path(LOCAL_DATASET_PATH)
    if not local_folder.is_absolute():
        # Относительно корня проекта
        project_root = Path(__file__).parent.parent
        local_folder = project_root / local_folder
    
    local_folder = local_folder.resolve()
    
    # Имя папки для назначения (берем последнюю часть пути)
    folder_name = local_folder.name
    
    # Полный путь назначения на сетевом диске
    destination_path = NETWORK_DATASET_PATH / folder_name
    
    print("=" * 60)
    print("ЗАГРУЗКА ДАТАСЕТА НА СЕТЕВОЙ ДИСК")
    print("=" * 60)
    print(f"Базовый путь: {NETWORK_BASE_PATH}")
    print(f"Папка датасетов: {NETWORK_DATASET_PATH}")
    print(f"Локальная папка: {local_folder}")
    print(f"Имя датасета: {folder_name}")
    print(f"Итоговый путь: {destination_path}")
    print("=" * 60)
    
    # Подтверждение
    confirm = input(f"\nЭто УДАЛИТ всё из {NETWORK_DATASET_PATH} и загрузит новые файлы. Продолжить? (y/n): ")
    if confirm.lower() != "y":
        print("Отменено.")
        sys.exit(0)
    
    # Удаляем содержимое папки dataset на сетевом диске
    print("\n" + "-" * 40)
    delete_folder_contents(NETWORK_DATASET_PATH)
    
    # Загружаем новую папку
    print("\n" + "-" * 40)
    success = upload_folder(local_folder, destination_path)
    
    if success:
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"Данные доступны по пути: {destination_path}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ЗАВЕРШЕНА С ОШИБКАМИ!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

