import os
from django.core.management.base import BaseCommand
from django.conf import settings
import boto3

class Command(BaseCommand):
    help = "Upload all files from MEDIA_ROOT into your S3/MinIO bucket"

    def handle(self, *args, **options):
        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=boto3.session.Config(signature_version='s3v4')
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for name in files:
                full_path = os.path.join(root, name)
                # key = path inside bucket, e.g. "restaurant_logos/kfc.png"
                key = os.path.relpath(full_path, settings.MEDIA_ROOT).replace(os.sep, '/')
                self.stdout.write(f"Uploading {key} …")
                s3.upload_file(full_path, bucket, key)
        self.stdout.write(self.style.SUCCESS("Done!"))
