import boto3
import time
from botocore.exceptions import ClientError

from .settings import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


def upload_avatar_to_s3(user_email, avatar_file):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket_name = AWS_STORAGE_BUCKET_NAME
    folder_name = 'profile'
    file_name = user_email + '.jpg'

    # Видалення попереднього аватара, якщо він існує
    try:
        s3.delete_object(Bucket=bucket_name, Key=f'{folder_name}/{file_name}')
    except ClientError as e:
        print(e)
        pass

    # Завантаження нового аватара
    try:
        s3.upload_fileobj(avatar_file, bucket_name, f'{folder_name}/{file_name}')
        timestamp = int(time.time() * 1000)
        image_url = f'https://{bucket_name}.s3.amazonaws.com/{folder_name}/{file_name}?timestamp={timestamp}'

        return image_url
    except ClientError as e:
        print(e)
        return None
