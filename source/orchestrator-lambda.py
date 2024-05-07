import json
import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError

promptTemplate = """\n\nHuman: You are a summarisation assistant. Your task is to summarise a call transcription between an agent and a customer.
Create a JSON document with the following fields:
call_summary - A summary of the call in less than 250 words
overall_sentiment_score - The overall sentiment of the call on a scale of 1-10
overall_sentiment - The overall sentiment of the call. This should be positive, negative or neutral
overall_sentiment_confidence - How confident you are about the overall sentiment on a scale of 0 to 1
customer_sentiment - The customer sentiment of the call. This should be positive, negative or neutral
agent_sentiment - The agent sentiment of the call. This should be positive, negative or neutral
customer_sentiment_confidence - How confident you are about the customer sentiment on a scale of 0 to 1
agent_sentiment_confidence - How confident you are about the agent sentiment on a scale of 0 to 1
agent_action_items - A list of action items for the agent from the call
customer_action_items - A list of action items for the customer from the call
Your output should be raw JSON - do not include any sentences or additional text outside of the JSON object.
Here is the call that I want you to summarise:
{transcript}
\n\nAssistant:"""

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    # Read the transcript from S3
    print("Reading from S3")
    s3 = boto3.resource("s3")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    # save the txt file object to a string variable
    data = s3.Object(bucket, object_key).get()['Body'].read().decode('utf-8')

    print("Read from S3")

    # Add the reviews to the LLM prompt
    prompt = promptTemplate.format(transcript=data)
    
    # Invoke the LLM
    print("Invoking bedrock")
    bedrock = boto3.client("bedrock-runtime", region_name="us-west-2") # Bedrock is not currently available in all regions
    # Invoke Claude 3 with the text prompt
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    try:
        response = bedrock.invoke_model(
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0,
                "top_p": 0.8,
                "top_k": 250
            }),
            contentType="application/json",
            accept="application/json",
            modelId=model_id
        )
        print("Response received from bedrock")
        print ("response from bedrock", response)
        
        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")
        print ("output_list ", output_list)
        print(f"- The model returned {len(output_list)} response(s):")
        
        
        analysis = json.loads(output_list[0].get("text"))
        print ("response_body", analysis)
        
        # Store the analysis in DynamoDB
        print("Saving to DynamoDB")
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
        table.put_item(
            Item={
                's3_uri': f"s3://{bucket}/{object_key}",
                'date': datetime.today().strftime('%d-%m-%Y'),
                'create_time': datetime.today().strftime('%d-%m-%YT%H:%M:%S'),
                'customer_sentiment': analysis["customer_sentiment"],
                'agent_sentiment': analysis["agent_sentiment"],
                'overall_sentiment': analysis["overall_sentiment"],
                'overall_sentiment_score': int(analysis["overall_sentiment_score"]),
                'overall_sentiment_confidence': str(analysis["overall_sentiment_confidence"]),
                'customer_sentiment_confidence': str(analysis["customer_sentiment_confidence"]),
                'agent_sentiment_confidence': str(analysis["agent_sentiment_confidence"]),
                'agent_action_items': json.dumps(analysis["agent_action_items"]),
                'customer_action_items': json.dumps(analysis["customer_action_items"]),
                'call_summary': analysis["call_summary"],
            }
        )
        print("Saved to DynamoDB")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully analysed customer call')
        }
    except ClientError as err:
        print(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        logger.error(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
