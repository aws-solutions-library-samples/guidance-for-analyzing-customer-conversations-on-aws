# Solution Guidance for Analyzing Customer Conversation on AWS





## Table of Content (required)

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

***Optional***

8. [FAQ, known issues, additional considerations, and limitations](#faq-known-issues-additional-considerations-and-limitations-optional)
9. [Revisions](#revisions-optional)
10. [Notices](#notices-optional)
11. [Authors](#authors-optional)

## Overview

This Guidance helps organizations harness the power of voice analytics to improve customer satisfaction. By automatically transcribing and analyzing customer service phone calls, companies can uncover valuable insights that were previously difficult to access. The goal is to provide a data-driven approach to understanding the voice of the customer and identifying key pain points or opportunities to enhance the customer experience.

Rather than relying on anecdotal feedback or manual review of call recordings, this solution leverages speech-to-text and natural language processing to automate the transcription and analysis process. This not only saves significant time and resources, but also provides deeper, more comprehensive insights that can inform strategic business decisions.
By turning customer conversations into actionable data, this Guidance empowers companies to make informed, customer-centric decisions that drive satisfaction and loyalty.

## Solution Overview

The solution is an implementation of customer conversation analytics, based on transcription and analysis of customer service phone conversations and customer chat. To enable customer conversation analysis, we first need to automatically transcribe the audio recordings of customer service calls using speech-to-text technology. The transcribed text is then analyzed using Claude 3 Haiku model to generate the call/transcript summary, overall sentiment of agent and customer, action items, and confidence scores. These insights are stored in a Dynamo db database to be used for generating reports and triggering email notifications for negative sentiments, allowing management to better understand customer pain points and opportunities to enhance the customer experience.


## Conversation Analysis Architecture

![image](https://github.com/aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws/blob/main/assets/Conversation%20Analysis.png)

1. Use Amazon Simple Storage(Amazon S3) to store the call recordings from source
2. Use Amazon Simple Storage(Amazon S3) to store the chat messages from source
3. An Amazon Simple Storage(Amazon S3) event notication invokes an AWS Lambda which transcribes the recording using  Amazon Transcribe and stores the transcription in Amazon Simple Storage(Amazon S3)
4. An AWS Lambda function retrieves the transcription from Amazon Simple Storage(Amazon S3)  and generates a call summary using the Foundation Model in Amazon Bedrock.
5. AWS Lambda persists the output from Amazon Bedrock like call/transcript summary, overall sentiment of agent and customer ,action items and confidence scores in Amazon DynamoDB
Amazon EventBridge Scheduler invokes an AWS Lambda function once a day to generate the report of the call summary and call sentiments updated in Amazon DynamoDB within the past 24 hours.
6. AWS Lambda generates the reports of negative sentiments and stores them in Amazon Simple Storage(Amazon S3) 
7. An Amazon Simple Storage(Amazon S3) event notification triggers an Amazon SNS notification once the CSV file report is generated and sends an email to the required recipient 
8. Optionally use Amazon Quick Sight to build business dashboards for monitoring about the services over time

## AWS services used
- Amazon Transcribe
- AWS Lambda
- Amazon Bedrock
- Amazon S3
- Amazon DynamoDB
- Amazon SNS
- Amazon EventBridge
- Amazon CloudWatch

## Prerequisites

1. [Bedrock Model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for Claude 3 Haiku Model

   
### Cost ( required )

This section is for a high-level cost estimate. Think of a likely straightforward scenario with reasonable assumptions based on the problem the Guidance is trying to solve. Provide an in-depth cost breakdown table in this section below ( you should use AWS Pricing Calculator to generate cost breakdown ).

Start this section with the following boilerplate text:

_You are responsible for the cost of the AWS services used while running this Guidance. As of <month> <year>, the cost for running this Guidance with the default settings in the <Default AWS Region (Most likely will be US East (N. Virginia)) > is approximately $<n.nn> per month for processing ( <nnnnn> records )._

Replace this amount with the approximate cost for running your Guidance in the default Region. This estimate should be per month and for processing/serving resonable number of requests/entities.

Suggest you keep this boilerplate text:
_We recommend creating a [Budget](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) through [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) to help manage costs. Prices are subject to change. For full details, refer to the pricing webpage for each AWS service used in this Guidance._

### Sample Cost Table ( required )

**Note : Once you have created a sample cost table using AWS Pricing Calculator, copy the cost breakdown to below table and upload a PDF of the cost estimation on BuilderSpace.**

The following table provides a sample cost breakdown for deploying this Guidance with the default parameters in the US East (N. Virginia) Region for one month.

| AWS service  | Dimensions | Cost [USD] |
| ----------- | ------------ | ------------ |
| Amazon Transcribe| 1000 calls per month each call 10 minutes(1000*10 minutes)  | $ 240 month |
| Amazon S3| 50 GB with Standard Storage | $ 1.15 month |
| AWS Lambda| <no of requestes  per month>  | $  |
| Amazon Bedrock |  | $ 0.00 |
| Amazon DynamoDB|  | $ 3.50month |
| Amazon SNS|  | $ 0.00 |
| Amazon EventBridge|  | $ 0.00 |


## Prerequisites (required)

### Operating System (required)

- Talk about the base Operating System (OS) and environment that can be used to run or deploy this Guidance, such as *Mac, Linux, or Windows*. Include all installable packages or modules required for the deployment. 
- By default, assume Amazon Linux 2/Amazon Linux 2023 AMI as the base environment. All packages that are not available by default in AMI must be listed out.  Include the specific version number of the package or module.

**Example:**
“These deployment instructions are optimized to best work on **<Amazon Linux 2 AMI>**.  Deployment in another OS may require additional steps.”

- Include install commands for packages, if applicable.


### Third-party tools (If applicable)

*List any installable third-party tools required for deployment.*


### AWS account requirements (If applicable)

*List out pre-requisites required on the AWS account if applicable, this includes enabling AWS regions, requiring ACM certificate.*

**Example:** “This deployment requires you have public ACM certificate available in your AWS account”

**Example resources:**
- ACM certificate 
- DNS record
- S3 bucket
- VPC
- IAM role with specific permissions
- Enabling a Region or service etc.


### aws cdk bootstrap (if sample code has aws-cdk)

<If using aws-cdk, include steps for account bootstrap for new cdk users.>

**Example blurb:** “This Guidance uses aws-cdk. If you are using aws-cdk for first time, please perform the below bootstrapping....”

### Service limits  (if applicable)

<Talk about any critical service limits that affect the regular functioning of the Guidance. If the Guidance requires service limit increase, include the service name, limit name and link to the service quotas page.>

### Supported Regions (if applicable)

<If the Guidance is built for specific AWS Regions, or if the services used in the Guidance do not support all Regions, please specify the Region this Guidance is best suited for>


## Deployment Steps (required)

The solution is deployed using a CloudFormation template, but as this relies on Python code files, the template must be packaged first.
To package the template:

1. Clone the repo using command ```git clone aws-solutions-library-samples/guidance-for-conversation-analysis-using-genai-on-aws```
2. cd to the repo folder ```cd guidance-for-conversation-analysis-using-genai-on-aws```
3. Create an S3 Bucket in the same region that you will deploy the solution from, noting the name.
4. From the directory containing the CloudFormation template and the Python code, run the following code, replacing `<S3 Bucket>` with the name of the bucket you created.  
`aws cloudformation package --template-file conversation-analysis-cfn-template.yml --s3-bucket <S3 Bucket> --output-template-file conversation-analysis-cfn-template.packaged.yml`  
This creates a packages template file, as well as uploading the code to S3, where it can used by the Lambda functions.

The packaged template file can then be deployed:
1. Navigate to the [CloudFormation console](https://console.aws.amazon.com/cloudformation) and choose 'Create Stack', 'With new resources'
2. Choose 'Template is ready' and 'Upload a template file', then upload the packaged template file.
3. On the next page, specify a name for the stack and an email to receive notifications at
4. Confirm the details on the next two pages and select 'Submit'

 
**Example:**

1. Clone the repo using command ```git clone xxxxxxxxxx```
2. cd to the repo folder ```cd <repo-name>```
3. Install packages in requirements using command ```pip install requirement.txt```
4. Edit content of **file-name** and replace **s3-bucket** with the bucket name in your account.
5. Run this command to deploy the stack ```cdk deploy``` 
6. Capture the domain name created by running this CLI command ```aws apigateway ............```



## Deployment Validation  (required)

<Provide steps to validate a successful deployment, such as terminal output, verifying that the resource is created, status of the CloudFormation template, etc.>

The deployment should be successful if all of the above steps complete without error. You can browse the resources created by navigating to the CloudFormation service in the AWS Console, finding the stack, and browsing its resources.

**Examples:**

* Open CloudFormation console and verify the status of the template with the name starting with xxxxxx.
* If deployment is successful, you should see an active database instance with the name starting with <xxxxx> in        the RDS console.
*  Run the following CLI command to validate the deployment: ```aws cloudformation describe xxxxxxxxxxxxx```



## Running the Guidance (required)

<Provide instructions to run the Guidance with the sample data or input provided, and interpret the output received.> 

This section should include:

* Guidance inputs
* Commands to run
* Expected output (provide screenshot if possible)
* Output description



## Next Steps (required)

Provide suggestions and recommendations about how customers can modify the parameters and the components of the Guidance to further enhance it according to their requirements.


## Cleanup (required)

- Include detailed instructions, commands, and console actions to delete the deployed Guidance.
- If the Guidance requires manual deletion of resources, such as the content of an S3 bucket, please specify.

The provisioned infrastructure can be deleted by deleting the CloudFormation stack. This will not remove any S3 buckets that are not empty, so it will be necessary to delete these from the S3 console first before deleting the CloudFormation stack.



## FAQ, known issues, additional considerations, and limitations (optional)


**Known issues (optional)**

<If there are common known issues, or errors that can occur during the Guidance deployment, describe the issue and resolution steps here>


**Additional considerations (if applicable)**

<Include considerations the customer must know while using the Guidance, such as anti-patterns, or billing considerations.>

**Examples:**

- “This Guidance creates a public AWS bucket required for the use-case.”
- “This Guidance created an Amazon SageMaker notebook that is billed per hour irrespective of usage.”
- “This Guidance creates unauthenticated public API endpoints.”


Provide a link to the *GitHub issues page* for users to provide feedback.


**Example:** *“For any feedback, questions, or suggestions, please use the issues tab under this repo.”*

## Revisions (optional)

Document all notable changes to this project.

Consider formatting this section based on Keep a Changelog, and adhering to Semantic Versioning.

## Notices (optional)

Include a legal disclaimer

**Example:**
*Customers are responsible for making their own independent assessment of the information in this Guidance. This Guidance: (a) is for informational purposes only, (b) represents AWS current product offerings and practices, which are subject to change without notice, and (c) does not create any commitments or assurances from AWS and its affiliates, suppliers or licensors. AWS products or services are provided “as is” without warranties, representations, or conditions of any kind, whether express or implied. AWS responsibilities and liabilities to its customers are controlled by AWS agreements, and this Guidance is not part of, nor does it modify, any agreement between AWS and its customers.*


## Authors (optional)

Name of code contributors
