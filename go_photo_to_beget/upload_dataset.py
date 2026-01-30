"""
Скрипт для загрузки датасета на S3 Beget.
Удаляет всё из BEGET_FOLDER/dataset/ и загружает новую папку.
"""

import os
import sys
import urllib3
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.config import Config

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загружаем .env
load_dotenv(Path(__file__).parent / ".env")

# Конфигурация S3
BEGET_URL = os.getenv("BEGET_URL")

BEGET_BUCKET = os.getenv("BEGET_NAME_BUCKET")
BEGET_ACCESS_KEY = os.getenv("BEGET_ACCESS_KEY")
BEGET_SECRET_KEY = os.getenv("BEGET_SECRET_KEY")
BEGET_PATH_STYLE = os.getenv("BEGET_PATH_STYLE", "true").lower() == "true"
BEGET_FOLDER = os.getenv("BEGET_FOLDER", "")

def get_s3_client():
    """Создает клиент S3 для Beget."""
    config = Config(
        s3={
            "addressing_style": "path" if BEGET_PATH_STYLE else "virtual",
        },
        signature_version="s3",  # Переключаемся на v2 для совместимости с Beget
    )
    
    return boto3.client(
        "s3",
        endpoint_url=BEGET_URL,
        aws_access_key_id=BEGET_ACCESS_KEY,
        aws_secret_access_key=BEGET_SECRET_KEY,
        config=config,
        verify=False,  # Отключаем проверку SSL для Beget
    )


def delete_folder_contents(s3_client, bucket: str, prefix: str):
    """Удаляет все объекты с указанным префиксом."""
    print(f"Удаление содержимого: {prefix}")
    
    paginator = s3_client.get_paginator("list_objects_v2")
    deleted_count = 0
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" not in page:
            print("Папка пуста или не существует.")
            return
        
        objects_to_delete = [{"Key": obj["Key"]} for obj in page["Contents"]]
        
        if objects_to_delete:
            #s3_client.delete_objects(
            #    Bucket=bucket,
            #    Delete={"Objects": objects_to_delete}
            #)
            deleted_count += len(objects_to_delete)
            print(f"  Удалено: {len(objects_to_delete)} объектов")
    
    print(f"Всего удалено: {deleted_count} объектов")


def upload_folder(s3_client, bucket: str, local_folder: Path, s3_prefix: str):
    """Загружает локальную папку на S3."""
    print(f"\nЗагрузка папки: {local_folder}")
    print(f"Назначение S3: {s3_prefix}")
    
    if not local_folder.exists():
        print(f"ОШИБКА: Папка {local_folder} не существует!")
        return False
    
    uploaded_count = 0
    
    for file_path in local_folder.rglob("*"):
        if file_path.is_file():
            # Относительный путь от локальной папки
            relative_path = file_path.relative_to(local_folder)
            # S3 ключ
            s3_key = f"{s3_prefix}/{relative_path.as_posix()}"
            
            print(f"  Загрузка: {relative_path} -> {s3_key}")
            
            try:
                # Используем put_object с Body в виде файла
                with open(file_path, "rb") as f:
                    s3_client.put_object(
                        Bucket=bucket,
                        Key=s3_key,
                        Body=f
                    )
                uploaded_count += 1
            except Exception as e:
                print(f"    ОШИБКА: {e}")
                return False
    
    print(f"\nВсего загружено: {uploaded_count} файлов")
    return True


def main():
    # Проверяем аргументы
    if len(sys.argv) < 2:
        print("Использование: python upload_dataset.py <путь_к_локальной_папке>")
        print("Пример: python upload_dataset.py learning/dataset/2026-01-30")
        sys.exit(1)
    
    local_folder_path = sys.argv[1]
    
    # Определяем абсолютный путь
    local_folder = Path(local_folder_path)
    if not local_folder.is_absolute():
        # Относительно корня проекта
        project_root = Path(__file__).parent.parent
        local_folder = project_root / local_folder
    
    local_folder = local_folder.resolve()
    
    # Имя папки для S3 (берем последнюю часть пути)
    folder_name = local_folder.name
    
    # Префикс на S3
    s3_dataset_prefix = f"{BEGET_FOLDER}/dataset" if BEGET_FOLDER else "dataset"
    s3_upload_prefix = f"{s3_dataset_prefix}/{folder_name}"
    
    print("=" * 60)
    print("ЗАГРУЗКА ДАТАСЕТА НА S3 BEGET")
    print("=" * 60)
    print(f"URL: {BEGET_URL}")
    print(f"Bucket: {BEGET_BUCKET}")
    print(f"Папка в S3: {s3_dataset_prefix}")
    print(f"Локальная папка: {local_folder}")
    print(f"Имя датасета: {folder_name}")
    print("=" * 60)
    
    # Подтверждение
    confirm = input("\nЭто УДАЛИТ всё из dataset/ на S3 и загрузит новые файлы. Продолжить? (y/n): ")
    if confirm.lower() != "y":
        print("Отменено.")
        sys.exit(0)
    
    # Подключаемся к S3
    print("\nПодключение к S3...")
    s3_client = get_s3_client()
    
    # Удаляем содержимое папки dataset
    print("\n" + "-" * 40)
    delete_folder_contents(s3_client, BEGET_BUCKET, s3_dataset_prefix + "/")
    
    # Загружаем новую папку
    print("\n" + "-" * 40)
    success = upload_folder(s3_client, BEGET_BUCKET, local_folder, s3_upload_prefix)
    
    if success:
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"Данные доступны по пути: {s3_upload_prefix}/")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ЗАВЕРШЕНА С ОШИБКАМИ!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()

