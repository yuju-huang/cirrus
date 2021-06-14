import boto3
import io

BUCKET = "criteo-kaggle-19b"
#BUCKET = "cirrus-bucket-390693756238"
KEY = "0"
#KEY = "test"
REGION = "us-east-2"

OUT_NAME = "s3_out"

def get_s3_object():
    s3 = boto3.client("s3", REGION)
    f = io.BytesIO()
#    s3.download_file(BUCKET, KEY, OUT_NAME)
    s3.download_fileobj(BUCKET, KEY, f)
    f.seek(0)
    print(f.read())

if __name__ == "__main__":
    get_s3_object()
