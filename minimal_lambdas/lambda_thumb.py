# reference: https://docs.aws.amazon.com/lambda/latest/dg/with-s3-tutorial.html
import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image
            
s3_client = boto3.client('s3')
            
def resize_image(image_path, resized_path):
  with Image.open(image_path) as image:
    image.thumbnail(tuple(x / 2 for x in image.size))
    image.save(resized_path)

 #  involed when when a file is uploaded to the s3 bucket
def lambda_handler(event, context):
  if "detail" in event:
    bucket = event['detail']['bucket']['name']
    key = unquote_plus(event['detail']['object']['key'])
    filename = os.path.basename(key)  
    tmpkey = filename
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
    upload_path = '/tmp/resized-{}'.format(tmpkey)
    s3_client.download_file(bucket, key, download_path)
    resize_image(download_path, upload_path)
    # store the resized image in the same bucket but in a thumbnails folder
    s3_client.upload_file(upload_path, bucket,  f"thumbnails/{filename}" )
    