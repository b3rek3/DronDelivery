# core/management/commands/create_minio_bucket.py
import json
from django.core.management.base import BaseCommand
import boto3
from django.conf import settings

class Command(BaseCommand):
    help = "Create the MinIO bucket (and make it public)"

    def handle(self, *args, **opts):
        endpoint = settings.AWS_S3_ENDPOINT_URL
        key = settings.AWS_ACCESS_KEY_ID
        secret = settings.AWS_SECRET_ACCESS_KEY
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        s3 = boto3.resource(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )

        # create if missing
        try:
            s3.meta.client.head_bucket(Bucket=bucket)
            self.stdout.write(self.style.NOTICE(f"Bucket “{bucket}” already exists"))
        except Exception:
            self.stdout.write(f"Creating bucket “{bucket}”…")
            s3.create_bucket(Bucket=bucket)

        # now set it public
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"]
                }
            ]
        }
        s3.meta.client.put_bucket_policy(
            Bucket=bucket,
            Policy=json.dumps(policy)
        )
        self.stdout.write(self.style.SUCCESS(f"Bucket “{bucket}” is now public"))
