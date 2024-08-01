# Solution Guidance for Analyzing Customer Conversation on AWS





## Table of Contents

List the top-level sections of the README template, along with a hyperlink to the specific section.

### Required

1. [Overview](#overview)
    - [Cost](#cost)
2. [Prerequisites](#prerequisites)
    - [Operating System](#operating-system)
3. [Deployment Steps](#deployment-steps)
4. [Deployment Validation](#deployment-validation)
5. [Running the Guidance](#running-the-guidance)
6. [Next Steps](#next-steps)
7. [Cleanup](#cleanup)
8. [Authors](#authors)


## Overview

This Guidance helps retail organizations harness the power of voice and chat analytics to improve customer satisfaction and loyalty. By automatically transcribing and analyzing customer service phone calls as well as online chat interactions, retailers can uncover valuable insights that were previously difficult to access.

The goal is to provide a data-driven approach to truly understanding the voice of the retail customer. This allows identification of key pain points or opportunities to enhance the overall shopping experience - from the customer's perspective.

Rather than relying solely on anecdotal feedback or manual review of call/chat logs, this solution leverages speech-to-text and natural language processing to automate the transcription and analysis process. This not only saves significant time and resources for retail teams, but also provides deeper, more comprehensive insights that can directly inform strategic business decisions.

By turning rich customer conversations into actionable data, this solution empowers retailers to make informed, customer-centric decisions that drive satisfaction, loyalty, and ultimately, sales growth

## Solution Overview

This solution provides comprehensive customer conversation analytics, leveraging transcription and analysis of both customer service phone calls and online chat interactions.

To enable this analysis, the system first automatically transcribes audio recordings of customer calls using Amazon Transcribe.The transcribed text from voice calls and text messages from the chat conversations, are then analyzed using the foundation model to generate valuable insights - including conversation summary, overall sentiment of both the agent and customer, derived action items from the conversation, and foundation model confidence scores on the sentiment scores.

These insights are stored in a DynamoDB table, empowering retailers generate reports and send email notifications to the cencerned teams, so they can review the analysis results of conversations whose sentiment scores are below the preset threshold. This helps retail management to better understand customer pain points, and uncover opportunities to enhance the overall shopping experience for customers.


## Conversation Analysis Architecture

![image](https://github.com/aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws/blob/main/assets/Conversation%20Analysis.png)

1a.Amazon Simple Storage Service (Amazon S3) is used to store the contact center chat transcripts as text files.

1b.The contact center call recordings are stored on another Amazon S3 storage bucket, which is configured to call an AWS Lambda function when an object is created.

2.AWS Lambda function uses Amazon Transcribe to convert the audio call into a text file and stores the resultant text files in the output S3 location.
  
3.The S3 buckets storing text transcripts (step 1.a) and output of Amazon Transcribe (step 2), are configured to call an AWS Lambda when a new object is available. This Lambda function uses Amazon Bedrock hosted Anthropic Claude 3 Sonnet model to generate summary and sentiment of the contact center conversations in the input file. This function also uses a prompt template that can be customized as needed to control input context passed to the foundation models.

4.AWS Lambda then parses the JSON output from Amazon Bedrock and persists the key details like conversation summary, customer and agent sentiments, confidence scores and action items derived from the conversations in Amazon DynamoDB.
  
5.A time triggered Amazon EventBridge scheduler calls another AWS Lambda function at a pre-set time. 
  
6.The AWS Lambda function reads the data from Amazon DynamoDB to generate a CSV file with the analysis results of the contact center conversations in the past 24 hours, whose sentiment scores are below a pre-defined threshold. This CSV file is then stored on Amazon S3.
    
7.Amazon S3, then triggers an event to call Amazon Simple Notification Service, which sends an email to the subscribed users. These business users, can review the analysis results and take necessary actions to improve the customer experiences.
   


## AWS services used
- Amazon Transcribe
- AWS Lambda
- Amazon Bedrock
- Amazon S3
- Amazon DynamoDB
- Amazon SNS
- Amazon EventBridge
- Amazon CloudWatch
   
### Cost

_You are responsible for the cost of the AWS services used while running this Guidance. As of May 2024, the cost for running this Guidance with the default settings in the us-east-1 region is approximately $300 per month for processing 1000 calls that average 10 minutes in length._

_We recommend creating a [Budget](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) through [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) to help manage costs. Prices are subject to change. For full details, refer to the pricing webpage for each AWS service used in this Guidance._

### Sample Cost Table

**Note : Once you have created a sample cost table using AWS Pricing Calculator, copy the cost breakdown to below table and upload a PDF of the cost estimation on BuilderSpace.**

The following table provides a sample cost breakdown for deploying this Guidance with the default parameters in the US East (N. Virginia) Region for one month.

| AWS service  | Dimensions | Cost [USD] |
| ----------- | ------------ | ------------ |
| Amazon Transcribe| 10,00 calls per month with each call 10 minutes (1000*10 minutes) + PII redaction  | $ 264 month |
| Amazon S3| 50 GB with Standard Storage | $ 1.15 month |
| AWS Lambda| 3000 invocations per month | $ 0.03 month  |
| Amazon Bedrock | Anthropic Claude 3 Sonnet - 1M input & output tokens per month | $ 18 month |
| Amazon DynamoDB| 50GB storage,Average item size 100 KB  | $ 12.50 month |
| Amazon SNS| 1000 email notifications per month | $ 0.00 |
| Amazon EventBridge| 1000 invocations per month | $ 0.00 |


## Prerequisites

This deployment requires you to have access to the Claude 3 Sonnet model. This can be requested through the Bedrock console as per the [Bedrock Model access instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).

Ensure the AWS CLI is installed using the [following instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

### Operating System

There are no specific operating system requirements. These deployment instructions can be deployed from a local machine or using a pre-configured Amazon Linux 2023 AWS Cloud9 development environment. Refer to the [Individual user setup for AWS Cloud9](https://docs.aws.amazon.com/cloud9/latest/user-guide/setup-express.html) for more information on how to set up Cloud9 as a user in the AWS account.

## Deployment Steps

The solution is deployed using a CloudFormation template, but as this relies on Python code files, the template must be packaged first.
To package the template:

1. Clone the repo using command 
```
git clone https://github.com/aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws.git
```
2. Navigate to the source directory
```
cd guidance-for-conversation-analysis-using-genai-on-aws/source
```
3. Create an S3 Bucket in the same region that you will deploy the solution from, noting the name. Instructions for creating an S3 bucket can be found [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).
4. From the directory containing the CloudFormation template and the Python code, run the following code, replacing `<S3 Bucket>` with the name of the bucket you created.  
```
aws cloudformation package --template-file conversation-analysis-cfn-template.yml --s3-bucket <S3 Bucket> --output-template-file conversation-analysis-cfn-template.packaged.yml
```
This creates a packages template file, as well as uploading the code to S3, where it can used by the Lambda functions.

The packaged template file can then be deployed:
1. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation) and choose 'Create Stack', 'With new resources'
2. Choose 'Template is ready' and 'Upload a template file', then upload the packaged template file.
3. On the next page, specify a name for the stack and an email to receive notifications to. You will also need to specify a sentiment threshold whereby any conversations below this sentiment threshold will be included in the daily email report.
4. Leave all settings as default on the next two pages and click 'Submit'


## Deployment Validation

The deployment has completed successfully if all of the above steps complete without error. To validate successful deployment:

1. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation)
2. Find the stack named [CFN Stack Name]
3. Verify status shows “CREATE_COMPLETE”


## Running the Guidance

Let's consider an example where a customer contacts customer-support to report a lost card. You decide to deploy this guidance to receive daily reports on calls where the overall sentiment is negative (i.e. a sentiment threshold below 5) and capture details about the call such as the agent and customer sentiment, summary of the call and action items from the call for both the agent and customer.

1. Place the call recording in the Audio Files bucket. Alternatively, if you have chat transcripts, place them in the Transcripts bucket.
2. From the root of the project, navigate to the sample-files directory. In this directory is a sample call recording named demo-call.mp3
```
cd guidance-for-conversation-analysis-using-genai-on-aws/sample-files
```

3. Using the AWS CLI s3 [cp](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/cp.html) command, upload the sample call recording to the audio files S3 bucket.
```
aws s3 cp demo-call.mp3 s3://<bucket-name>
```
Replace bucket-name with the name of the audio files s3 bucket which was created while deploying the CloudFormation stack. To find this, navigate to the CloudFormation console, click on the stack you created for this project, click on the “Resources” tab, find the line item with the logical ID “AudioFilesBucket”, the “Physical ID” is the name of the bucket. 


2. After 3-5 minutes, you can view the outputs for the call in the created DynamoDB table which will capture details such as the agent and customer sentiment, summary of the call and action items from the call for both the agent and customer. The DynamoDB table can be located in the Resources tab in the CloudFormation console, with the logical ID "AnalysisTable". An example screenshot of the table in the DynamoDB console is shown below.\
![image](assets/DynamoDB%20Table.png)

3. You will receive an email from AWS asking you to confirm your SNS subscription. Click "Confirm subscription" in the email.

4. By default this guidance is configured to have a daily report of sentiment that falls below the defined threshold. However, to showcase this feature, you can also trigger a manual report generation by manually triggering the "NotificationLambda" function.

4. Navigate to the CloudFormation console, click on the stack you created for this project, click on the “Resources” tab, find the line item with the logical ID “NotificationLambda” and click the hyperlink in the physical ID column to navigate to the lambda console.

5. Click "Test" and enter "DemoEvent" for the "Event Name" field.

6. Copy and past the following for the event JSON and click "Save".
```json
{
  "env": "demo"
}
```
7. Click "Test" and that will trigger an email with all reports in the database that fall below the sentiment threshold.
![image](assets/Notification%20Lambda.png)


4. You can optionally visualise the DynamoDB databse in QuickSight to gain insights on common complaints from customers and frequent agent action items to identify areas for optimization.


## Next Steps

You can adjust the sentiment threshold that controls when a conversation is added to the daily report and the email address to which notifications are sent. This can be updated by:

1. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation)
2. select the stack named [CFN Stack Name]
3. Click Update
4. Click Next
5. Update the SentimentThresholdParameter and click Next
6. Leave all other settings as default and submit the changes.

You can also extend this guidance by using the Athena DynamoDB connector with QuickSight to visualise the conversation analysis results over time.

## Cleanup

1. Follow the [instructions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/empty-bucket.html) to empty all the S3 buckets that were deployed by this stack
2. Repeat the above step for the S3 bucket you created in Step 3 of the [Deployment steps](#deployment-steps).
3. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation)
4. Select the stack named [CFN Stack Name]
5. In the stack details pane, choose Delete.
6. Select Delete stack when prompted.

Cleanup is complete when the stack is in the DELETE_COMPLETE state.

## Authors

Ariq Rahman\
Sujata Singh\
Rajesh Sripathi
