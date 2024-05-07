import boto3
import json
import os

def lambda_handler(event, context):
    output_bucket = os.environ.get('OUTPUT_BUCKET')
    input_bucket = event["Records"][0]["s3"]["bucket"]["name"] 
    object_key = event["Records"][0]["s3"]["object"]["key"]
    output_key = object_key.split('.')[0] + ".txt"

    if object_key.endswith('.temp'):
        return {
        'statusCode': 200,
        'body': json.dumps('Skipping temp file')
        }

    # Get the file from S3
    s3_client = boto3.client('s3')
    file_object = s3_client.get_object(Bucket=input_bucket, Key=object_key)["Body"]
    data = json.loads(file_object.read())

    s3_client.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=parse_transcribe_response(data),
        ContentType='text/plain'
        )

    return {
    'statusCode': 200,
    'body': json.dumps(f'{object_key} Transcript saved!')
    }


def parse_transcribe_response(response):

    lines = []
    line = ''
    speaker = 'spk_1'
    most_recent_speaker = 'spk_1'

    # Loop through the speakers and add them to the transcription.
    items = response['results']['items']
    for item in items:
        if item.get('start_time'):  # This is a spoken item
 
            speaker = item.get('speaker_label', most_recent_speaker) # assume prv speaker if speaker label not present

            if speaker == most_recent_speaker:
                # Append the content to line and repeat
                line+=f" {item['alternatives'][0]['content']}"

            else:
                # New speaker
                lines.append(f'{line}')
                most_recent_speaker = speaker
                line=f"{speaker}: {item['alternatives'][0]['content']}"

        elif item['type'] == 'punctuation':
            line+=item['alternatives'][0]['content']

    lines.append(line)
    
    return '\n\n'.join(lines)