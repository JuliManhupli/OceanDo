import boto3
from botocore.exceptions import ClientError
from tasks.models import File, Task

from .settings import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def upload_avatar_to_s3(user_email, avatar_file):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket_name = AWS_STORAGE_BUCKET_NAME
    file_name = f'{user_email}.jpg'
    file_path = f'avatars/{file_name}'

    try:
        # Видалення попереднього аватара, якщо він існує
        s3.delete_object(Bucket=bucket_name, Key=file_path)

        # Завантаження нового аватара
        s3.upload_fileobj(avatar_file, bucket_name, file_path)
        return file_path
    except ClientError as e:
        print(e)
        return None


def delete_avatar_from_s3(user_email):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket_name = AWS_STORAGE_BUCKET_NAME
    file_name = f'{user_email}.jpg'
    file_path = f'avatars/{file_name}'

    try:
        # Видалення аватара
        s3.delete_object(Bucket=bucket_name, Key=file_path)
    except ClientError as e:
        print(e)
        return None


def upload_file_to_s3(file, task_id):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket_name = AWS_STORAGE_BUCKET_NAME
    task_folder = f'tasks/{task_id}/'
    file_name = file.name
    file_path = task_folder + file_name

    s3.upload_fileobj(file, bucket_name, file_path)

    file_instance = File.objects.create(
        title=file_name,
        file=file_path
    )

    # Додати файл до завдання
    task = Task.objects.get(pk=task_id)
    task.files.add(file_instance)

    return file_instance
