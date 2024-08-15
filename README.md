Software Approval Process via email
======================================================

Features
========

1. Lambda Downloads CVE's and Approved software list and stores in S3 in queriable format from Athena
2. User submits api gateway request for software approval with
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
* Lambda checks RDS for CVEs which apply to the software
* If there are CVE, checks the approved CVEs to determine if already approved
* If not approved, sends email to approver


4. Approver receives email and approves or denies

5. API Gateway receives approved or deny request
* Review pending approved software matching token and updates RDS table
* NOTE:  Checks approved software database, in-case someone else has already approved the software.


Setup
=====
1. Update variables.tf
2. Run main.py

