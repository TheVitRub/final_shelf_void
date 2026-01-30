"""
Скрипт для скачивания (вытаскивания) датасета с сетевого диска.
Забирает папку из T:\\Рябов\\learning\\dataset\\ и сохраняет в локальную learning\\dataset\\.
"""

import sys
import shutil
from pathlib import Path

# --- НАСТРОЙКИ ---
# Имя папки, которую хотим забрать с сетевого диска
FOLDER_NAME = "2026-01-30_v1" # <--- МЕНЯТЬ ИМЯ ПАПКИ ТУТ

# Конфигурация сетевого диска (Откуда берем)
NETWORK_BASE_PATH = Path(r"T:\Рябов\learning")
NETWORK_DATASET_PATH = NETWORK_BASE_PATH / "dataset" / FOLDER_NAME

# Локальная конфигурация (Куда сохраняем)
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_DATASET_ROOT = PROJECT_ROOT / "learning" / "dataset"
LOCAL_TARGET_PATH = LOCAL_DATASET_ROOT / FOLDER_NAME
# -----------------

def main():
    print("=" * 60)
    print("СКАЧИВАНИЕ ДАТАСЕТА С СЕТЕВОГО ДИСКА")
    print("=" * 60)
    print(f"Источник (Диск): {NETWORK_DATASET_PATH}")
    print(f"Назначение (Локально): {LOCAL_TARGET_PATH}")
    print("=" * 60)

    # 1. Проверяем, существует ли папка на диске
    if not NETWORK_DATASET_PATH.exists():
        print(f"ОШИБКА: Папка {NETWORK_DATASET_PATH} не найдена на сетевом диске!")
        sys.exit(1)

    # 2. Подтверждение
    confirm = input(f"\nЭто заменит локальную папку {FOLDER_NAME} данными с диска. Продолжить? (y/n): ")
    if confirm.lower() != "y":
        print("Отменено.")
        sys.exit(0)

    # 3. Если локальная папка уже есть, удаляем её перед копированием
    if LOCAL_TARGET_PATH.exists():
        print(f"\nУдаление старой локальной папки: {LOCAL_TARGET_PATH}")
        try:
            shutil.rmtree(LOCAL_TARGET_PATH)
        except Exception as e:
            print(f"ОШИБКА при удалении: {e}")
            sys.exit(1)

    # 4. Копируем данные
    print(f"Копирование данных...")
    try:
        # Создаем родительскую папку learning/dataset, если её нет
        LOCAL_DATASET_ROOT.mkdir(parents=True, exist_ok=True)
        
        shutil.copytree(NETWORK_DATASET_PATH, LOCAL_TARGET_PATH)
        
        # Считаем файлы
        files_count = sum(1 for _ in LOCAL_TARGET_PATH.rglob("*") if _.is_file())
        
        print("\n" + "=" * 60)
        print("СКАЧИВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"Всего получено: {files_count} файлов")
        print(f"Путь: {LOCAL_TARGET_PATH}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА при копировании: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

