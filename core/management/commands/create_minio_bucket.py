import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Create the MinIO bucket if it does not already exist'

    def handle(self, *args, **options):
        endpoint = settings.AWS_S3_ENDPOINT_URL
        access   = settings.AWS_ACCESS_KEY_ID
        secret   = settings.AWS_SECRET_ACCESS_KEY
        bucket   = settings.AWS_STORAGE_BUCKET_NAME
        region   = settings.AWS_S3_REGION_NAME

        s3 = boto3.resource(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access,
            aws_secret_access_key=secret,
            config=Config(signature_version='s3v4'),
            region_name=region,
            use_ssl=False,
            verify=False,
        )

        try:
            s3.meta.client.head_bucket(Bucket=bucket)
            self.stdout.write(self.style.SUCCESS(f'Bucket "{bucket}" already exists'))
        except ClientError as e:
            code = int(e.response['Error']['Code'])
            # 404 Not Found or 403 Forbidden → create it
            if code in (404, 403):
                s3.create_bucket(Bucket=bucket)
                self.stdout.write(self.style.SUCCESS(f'Bucket "{bucket}" created'))
            else:
                self.stderr.write(self.style.ERROR(f'Unexpected error: {e}'))
                raise
