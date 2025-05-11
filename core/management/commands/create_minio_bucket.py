from django.core.management.base import BaseCommand
import boto3
import botocore
from django.conf import settings

class Command(BaseCommand):
    help = "Ensure the MinIO bucket exists"

    def handle(self, *args, **options):
        s3 = boto3.resource(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=botocore.client.Config(signature_version='s3v4'),
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        try:
            s3.meta.client.head_bucket(Bucket=bucket)
            self.stdout.write(self.style.SUCCESS(f"Bucket '{bucket}' already exists"))
        except botocore.exceptions.ClientError:
            s3.create_bucket(Bucket=bucket)
            self.stdout.write(self.style.SUCCESS(f"Bucket '{bucket}' created"))
