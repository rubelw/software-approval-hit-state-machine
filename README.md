Software Approval State Machine with Human-in-the-Loop
======================================================

Features
========

1. Downloads CVE's and Approved software list and stores in S3 in queriable format from Athena
2. User submits request for software approval
* Software vendor
* Software name\
* Requestor email
* Approver email
* Auth token as query parameter

```commandline
 curl -X POST   https://xxx.execute-api.us-east-1.amazonaws.com/test/mypath?authToken=xxxx   -H "Content-Type: application/json"   -d '{"Vendor": "Apache","Software":"airflow","Requestor":"xxx@gmail.com","Approver":"xxxx@gmail.com"}'

```


3. API Gateway
* Custom authorizer validates token
* Lambda checks dynamodb for CVEs which apply to the software
* If there are CVE, checks the approved CVEs to determine if already approved
* If not approved, executes stqte machine to get task token
* state machine sends output to SQS
* SQS triggers lambda to send email

4. User receives email and approves or denies

5. API Gateway receives approved or deny request
* Review pending approved software matching token and updates dynamodb table


Setup
=====
1. Update variables.tf
2. Run main.py

