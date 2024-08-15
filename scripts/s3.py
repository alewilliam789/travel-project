import logging
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv


    

def get_bucket():
    
    load_dotenv()
    
    region = os.environ.get("S3REGION")

    key = os.environ.get("S3KEY")

    value = os.environ.get("S3VALUE")

    name = os.environ.get("S3NAME")

    s3 = boto3.resource(
        service_name='s3',
        region_name=region,
        aws_access_key_id = key,
        aws_secret_access_key= value
    )
    
    return s3.Bucket(name)




def upload_file(file_name, object_name=None):
    
   
    if object_name is None:
        object_name = file_name
    
    bucket = get_bucket()

    try: 
        response = bucket.upload_file(Key=object_name,Filename=file_name)
    except ClientError as e:
        logging.error(e)
    else:
        logging.info(response)
    

def download_file(key,file_name):
    
    bucket = get_bucket()

    try:
        response = bucket.download_file(key,file_name)
    except ClientError as e:
        if(e.response['Error']['Code'] == "404"):
            logging.error("That object does not exist.")
        else:
            logging.error(e)



