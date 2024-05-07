import boto3
import json
import uuid
import os
 

def lambda_handler(event, context):
    print(event)
    input_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    transcribe_audio(input_bucket_name, object_key)
    
    return {
    'statusCode': 200,
    'body': json.dumps('Successfully started transcription job')
    }


def transcribe_audio(input_bucket_name, object_key):
    transcribe = boto3.client('transcribe')
    job_uri = f"s3://{input_bucket_name}/{object_key}"

    
    job_name = str(uuid.uuid4()) + "-" + object_key.split('.')[0]    

    transcribe.start_transcription_job(
        TranscriptionJobName = job_name,
        Media = {
            'MediaFileUri': job_uri
        },
        OutputBucketName = os.environ.get("OUTPUT_BUCKET"),
        LanguageCode = 'en-US', 
        Settings = {
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 2
        },
        ContentRedaction = {
            'RedactionType': 'PII',
            'RedactionOutput': 'redacted',
        }
    )