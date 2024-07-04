# Solution Guidance for Analyzing Customer Conversation on AWS





## Table of Contents (required)

List the top-level sections of the README template, along with a hyperlink to the specific section.

### Required

1. [Overview](#overview-required)
    - [Cost](#cost)
2. [Prerequisites](#prerequisites-required)
    - [Operating System](#operating-system-required)
3. [Deployment Steps](#deployment-steps-required)
4. [Deployment Validation](#deployment-validation-required)
5. [Running the Guidance](#running-the-guidance-required)
6. [Next Steps](#next-steps-required)
7. [Cleanup](#cleanup-required)


## Overview

This Guidance helps retail organizations harness the power of voice and chat analytics to improve customer satisfaction and loyalty. By automatically transcribing and analyzing customer service phone calls as well as online chat interactions, retailers can uncover valuable insights that were previously difficult to access.

The goal is to provide a data-driven approach to truly understanding the voice of the retail customer. This allows identification of key pain points or opportunities to enhance the overall shopping experience - from the customer's perspective.

Rather than relying solely on anecdotal feedback or manual review of call/chat logs, this solution leverages speech-to-text and natural language processing to automate the transcription and analysis process. This not only saves significant time and resources for retail teams, but also provides deeper, more comprehensive insights that can directly inform strategic business decisions.

By turning rich customer conversations into actionable data, this solution empowers retailers to make informed, customer-centric decisions that drive satisfaction, loyalty, and ultimately, sales growth

## Solution Overview

This solution provides comprehensive customer conversation analytics, leveraging transcription and analysis of both customer service phone calls and online chat interactions.

To enable this analysis, the system first automatically transcribes audio recordings of customer calls using Amazon Transcribe.The transcribed text from both voice calls and chat messages are then analyzed using the Claude 3 Sonnet model to generate valuable insights - including call/chat summaries, overall sentiment of both the agent and customer, identified action items, and confidence scores.

These insights are stored in a DynamoDB database, powering reporting and email notifications triggered by negative customer sentiments. This empowers retail management to better understand customer pain points across voice and digital channels, and uncover opportunities to enhance the overall shopping experience


## Conversation Analysis Architecture

![image](https://github.com/aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws/blob/main/assets/Conversation%20Analysis.png)

1a.Use Amazon Simple Storage(Amazon S3) to store the chat messages between a retail customer and a customer service agent. 

1b.Use  Amazon S3 to store the call recordings between a retail customer and a customer service agent. This could showcase typical inquiries from customers about product information, order status, returns, or other common retail-related topics.

2.An Amazon S3 event notication invokes an AWS Lambda which transcribes the recording using  Amazon Transcribe and stores the transcription in S3 Amazon S3
   
3.An AWS Lambda function retrieves the transcription from Amazon S3 and generates a call or chat messages summary using the Foundation Model in Amazon Bedrock. A pre-built Prompt Template is used in the Orchestration Lambda Function, which can be customized as needed.
  
4.AWS Lambda persists the output from Amazon Bedrock like call or chat summary, overall sentiment of agent and customer ,action items and confidence scores in Amazon DynamoDB
   
5.A daily AWS Lambda function is triggered by an Amazon EventBridge Scheduler. The EventBridge Cron schedule can be customized as needed to accommodate the business's preferences.
   
6.The AWS Lambda function generates a daily report of negative customer sentiment from voice calls and retail chat messages retrieved from Amazon DynamoDB in the previous 24 hours. This data is then pushed to an Amazon S3 bucket, empowering retail teams to promptly investigate and address underlying customer issues. The sentiment threshold triggering alerts can be customized via the  CloudFormation template, allowing the retail business to stay proactive in improving the overall customer experience.

    
7.An Amazon S3 event notifications trigger email alerts via Amazon SNS when a CSV report of negative customer sentiments is generated. The email includes a pre-signed S3 URL, allowing retail teams to quickly access the report. The SNS subscription recipients are customizable via CloudFormation, ensuring the insights reach the right stakeholders to promptly address customer issues
   
8.Optionally, use Amazon QuickSight to build business dashboards for comprehensive analysis and monitoring service performance over time, leveraging a prebuilt Amazon Athena DynamoDB connector(https://aws.amazon.com/blogs/big-data/visualize-amazon-dynamodb-insights-in-amazon-quicksight-using-the-amazon-athena-dynamodb-connector-and-aws-glue/)

## AWS services used
- Amazon Transcribe
- AWS Lambda
- Amazon Bedrock
- Amazon S3
- Amazon DynamoDB
- Amazon Athena
- Amazon SNS
- Amazon EventBridge
- Amazon CloudWatch

## Prerequisites

1. [Bedrock Model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for Claude 3 Sonnet Model

   
### Cost ( required )

This section is for a high-level cost estimate. Think of a likely straightforward scenario with reasonable assumptions based on the problem the Guidance is trying to solve. Provide an in-depth cost breakdown table in this section below ( you should use AWS Pricing Calculator to generate cost breakdown ).

Start this section with the following boilerplate text:

_You are responsible for the cost of the AWS services used while running this Guidance. As of May 2024, the cost for running this Guidance with the default settings in the us-east-1 region is approximately $300 per month for processing 1000 calls that average 10 minutes in length._

Suggest you keep this boilerplate text:
_We recommend creating a [Budget](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) through [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) to help manage costs. Prices are subject to change. For full details, refer to the pricing webpage for each AWS service used in this Guidance._

### Sample Cost Table ( required )

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


## Prerequisites (required)

This deployment requires you to have access to the Claude 3 Sonnet model. This can be requested through the Bedrock console.

## Deployment Steps (required)

The solution is deployed using a CloudFormation template, but as this relies on Python code files, the template must be packaged first.
To package the template:

1. Clone the repo using command ```git clone aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws```
2. Navigate to the source directory ```cd guidance-for-conversation-analysis-using-genai-on-aws/source```
3. Create an S3 Bucket in the same region that you will deploy the solution from, noting the name.
4. From the directory containing the CloudFormation template and the Python code, run the following code, replacing `<S3 Bucket>` with the name of the bucket you created.  
`aws cloudformation package --template-file conversation-analysis-cfn-template.yml --s3-bucket <S3 Bucket> --output-template-file conversation-analysis-cfn-template.packaged.yml`  
This creates a packages template file, as well as uploading the code to S3, where it can used by the Lambda functions.

The packaged template file can then be deployed:
1. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation) and choose 'Create Stack', 'With new resources'
2. Choose 'Template is ready' and 'Upload a template file', then upload the packaged template file.
3. On the next page, specify a name for the stack and an email to receive notifications to. You will also need to specify a sentiment threshold whereby any conversations below this sentiment threshold will be included in the daily email report.
4. Leave all settings as default on the next two pages and click 'Submit'


## Deployment Validation  (required)

The deployment completed successfully if all of the above steps complete without error. You can browse the resources created by navigating to the CloudFormation service in the AWS Console, finding the stack, and browsing its resources.


## Running the Guidance (required)

1. Place the audio files in the Audio Files bucket. Alternatively, if you have chat transcripts, place them in the Transcripts bucket.
2. You can view the outputs for the call in the created DynamoDB table which will capture details such as the agent and customer sentiment, summary of the call and action items from the call for both the agent and customer.
2. You will be emailed a daily report with all the conversations which fall below the defined sentiment threshold.


## Next Steps (required)

Provide suggestions and recommendations about how customers can modify the parameters and the components of the Guidance to further enhance it according to their requirements.


## Cleanup (required)

The provisioned infrastructure can be deleted by deleting the CloudFormation stack. This will not remove any S3 buckets that are not empty, so it will be necessary to empty these buckets from the S3 console first before deleting the CloudFormation stack.


## Authors (optional)

Name of code contributors
