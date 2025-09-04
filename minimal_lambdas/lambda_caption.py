import boto3  # AWS S3 SDK
import pymysql  # MySQL database connector
import google.generativeai as genai  # Gemini API for image captioning
import base64  # Encoding image data for API processing
from urllib.parse import unquote_plus
from botocore.exceptions import ClientError
import json

import time, logging, traceback
log = logging.getLogger()
log.setLevel(logging.INFO)

log.info("🔹1")

s3 = boto3.client('s3')

# Configure Gemini API, REPLACE with your Gemini API key
GOOGLE_API_KEY = 
genai.configure(api_key=GOOGLE_API_KEY)
# Choose a Gemini model for generating captions
model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-05-20")

log.info("🔹2")

def get_secret():
    secret_name = 
    region_name = 

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

secret = get_secret()
DB_USER, DB_PASSWORD = secret["username"], secret["password"]
DB_HOST = 
DB_NAME = 


def generate_image_caption(image_data):
    """
    Generate a caption for an uploaded image using the Gemini API.

    :param image_data: Raw binary image data
    :return: Generated caption or error message
    """
    try:
        encoded_image = base64.b64encode(image_data).decode("utf-8")
        response = model.generate_content(
            [
                {"mime_type": "image/jpeg", "data": encoded_image},
                "Caption this image.",
            ]
        )
        return response.text if response.text else "No caption generated."
    except Exception as e:
        return f"Error: {str(e)}"

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
     

def lambda_handler(event, context):
    log.info("🔹3")

    if "detail" in event:
        bucket = event['detail']['bucket']['name']
        key = unquote_plus(event['detail']['object']['key'])
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/lambda-proxy-binary-media.html
        file = s3.get_object(Bucket=bucket, Key=key)
        # file as binary data 
        file_data = file['Body'].read()

        log.info("🔹4")

        # Generate caption
        caption = generate_image_caption(file_data)
        # caption = "test caption 3rd" # test

        log.info("🔹5")

        # Save metadata to the database
        try:
            connection = get_db_connection()
            if connection is None:
                return {
                    "statusCode": 500,
                    "body": json.dumps({ "error": "DB connect failed" })
                    }
            cursor = connection.cursor()
            cursor.execute(
                    """
                    INSERT INTO captions (image_key, caption)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                    caption = VALUES(caption),
                    uploaded_at = CURRENT_TIMESTAMP
                    """,
                (key, caption),
            )
            connection.commit()
            connection.close()
            return {
                "statusCode": 200,
                "body": json.dumps({"image_key": key, "caption": caption})
                }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Database Error", "message": str(e)})
                }