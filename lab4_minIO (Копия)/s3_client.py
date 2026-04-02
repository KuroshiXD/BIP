#!/usr/bin/env python3
"""
Консольный клиент для S3-совместимого хранилища (MinIO).
Поддерживает:
  - create-bucket <bucket>
  - delete-bucket <bucket>
  - list-buckets
  - list-objects <bucket>
  - bucket-info <bucket>
  - object-info <bucket> <key>
  - upload <bucket> <file> [remote_key]
  - download <bucket> <key> [local_file]
"""

import sys
import os
import argparse
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Конфигурация подключения к MinIO
ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
USE_SSL = False

def get_s3_client():
    """Возвращает клиент S3 для MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        use_ssl=USE_SSL,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def create_bucket(bucket_name):
    s3 = get_s3_client()
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' успешно создан.")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def delete_bucket(bucket_name):
    s3 = get_s3_client()
    try:
        # Сначала удаляем все объекты в bucket (иначе MinIO не позволит удалить непустой bucket)
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            for obj in objects["Contents"]:
                s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
            print(f"Удалено {len(objects['Contents'])} объектов из bucket.")
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' успешно удалён.")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def list_buckets():
    s3 = get_s3_client()
    try:
        response = s3.list_buckets()
        buckets = [b["Name"] for b in response["Buckets"]]
        if buckets:
            print("Список bucket'ов:")
            for b in buckets:
                print(f"  - {b}")
        else:
            print("Нет bucket'ов.")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def list_objects(bucket_name):
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" not in response:
            print(f"Bucket '{bucket_name}' пуст.")
            return
        print(f"Объекты в bucket '{bucket_name}':")
        for obj in response["Contents"]:
            size_kb = obj["Size"] / 1024
            print(f"  - {obj['Key']} ({size_kb:.2f} KB, изменён: {obj['LastModified']})")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def bucket_info(bucket_name):
    s3 = get_s3_client()
    try:
        # Получаем информацию о bucket (дата создания, регион)
        # В MinIO нет прямого метода, используем head_bucket и доп. запросы
        s3.head_bucket(Bucket=bucket_name)
        # Для региона: берём из конфигурации расположения
        try:
            location = s3.get_bucket_location(Bucket=bucket_name)
            region = location["LocationConstraint"] or "us-east-1"
        except:
            region = "unknown"
        print(f"Bucket: {bucket_name}")
        print(f"  Регион: {region}")
        # Получаем количество объектов и общий размер
        objects = s3.list_objects_v2(Bucket=bucket_name)
        obj_count = objects.get("KeyCount", 0)
        total_size = sum(obj["Size"] for obj in objects.get("Contents", []))
        print(f"  Объектов: {obj_count}")
        print(f"  Общий размер: {total_size / (1024*1024):.2f} MB")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def object_info(bucket_name, object_key):
    s3 = get_s3_client()
    try:
        response = s3.head_object(Bucket=bucket_name, Key=object_key)
        print(f"Объект: {bucket_name}/{object_key}")
        print(f"  Размер: {response['ContentLength']} байт ({response['ContentLength']/1024:.2f} KB)")
        print(f"  ETag: {response['ETag']}")
        print(f"  Последнее изменение: {response['LastModified']}")
        print(f"  Content-Type: {response.get('ContentType', 'не указан')}")
        # Дополнительные метаданные, если есть
        metadata = response.get("Metadata", {})
        if metadata:
            print("  Пользовательские метаданные:")
            for k, v in metadata.items():
                print(f"    {k}: {v}")
    except ClientError as e:
        print(f"Ошибка: {e}", file=sys.stderr)

def upload_file(bucket_name, local_file, remote_key=None):
    if not os.path.isfile(local_file):
        print(f"Файл '{local_file}' не найден.", file=sys.stderr)
        return
    if remote_key is None:
        remote_key = os.path.basename(local_file)
    s3 = get_s3_client()
    try:
        s3.upload_file(local_file, bucket_name, remote_key)
        print(f"Файл '{local_file}' загружен в bucket '{bucket_name}' как '{remote_key}'.")
    except ClientError as e:
        print(f"Ошибка загрузки: {e}", file=sys.stderr)

def download_file(bucket_name, object_key, local_file=None):
    if local_file is None:
        local_file = object_key
    s3 = get_s3_client()
    try:
        s3.download_file(bucket_name, object_key, local_file)
        print(f"Объект '{bucket_name}/{object_key}' скачан в '{local_file}'.")
    except ClientError as e:
        print(f"Ошибка скачивания: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="S3 клиент для MinIO")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-bucket
    p_create = subparsers.add_parser("create-bucket", help="Создать bucket")
    p_create.add_argument("bucket", help="Имя bucket")

    # delete-bucket
    p_delete = subparsers.add_parser("delete-bucket", help="Удалить bucket (и все объекты в нём)")
    p_delete.add_argument("bucket", help="Имя bucket")

    # list-buckets
    subparsers.add_parser("list-buckets", help="Показать все bucket'ы")

    # list-objects
    p_list = subparsers.add_parser("list-objects", help="Список объектов в bucket")
    p_list.add_argument("bucket", help="Имя bucket")

    # bucket-info
    p_binfo = subparsers.add_parser("bucket-info", help="Метаинформация о bucket")
    p_binfo.add_argument("bucket", help="Имя bucket")

    # object-info
    p_oinfo = subparsers.add_parser("object-info", help="Метаинформация об объекте")
    p_oinfo.add_argument("bucket", help="Имя bucket")
    p_oinfo.add_argument("key", help="Ключ объекта")

    # upload
    p_up = subparsers.add_parser("upload", help="Загрузить файл в bucket")
    p_up.add_argument("bucket", help="Имя bucket")
    p_up.add_argument("file", help="Путь к локальному файлу")
    p_up.add_argument("remote_key", nargs="?", help="Ключ объекта в хранилище (по умолчанию – имя файла)")

    # download
    p_down = subparsers.add_parser("download", help="Скачать объект из bucket")
    p_down.add_argument("bucket", help="Имя bucket")
    p_down.add_argument("key", help="Ключ объекта")
    p_down.add_argument("local_file", nargs="?", help="Локальное имя файла (по умолчанию – ключ объекта)")

    args = parser.parse_args()

    if args.command == "create-bucket":
        create_bucket(args.bucket)
    elif args.command == "delete-bucket":
        delete_bucket(args.bucket)
    elif args.command == "list-buckets":
        list_buckets()
    elif args.command == "list-objects":
        list_objects(args.bucket)
    elif args.command == "bucket-info":
        bucket_info(args.bucket)
    elif args.command == "object-info":
        object_info(args.bucket, args.key)
    elif args.command == "upload":
        upload_file(args.bucket, args.file, args.remote_key)
    elif args.command == "download":
        download_file(args.bucket, args.key, args.local_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()