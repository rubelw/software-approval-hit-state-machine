import json
import boto3
import os
import re
import time

from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

# Sends email to the user
def lambda_handler(event, context):
    print('event: '+str(event))
    print('context: '+str(context))

    if 'Records' in event:
        print('Records in event')
        if 'body' in event['Records'][0]:
            print('body in Records')

            data = json.loads(event['Records'][0]['body'])
            print('data: ' + str(data))

            if 'token' in data['input']:
                token = data['input']['token']
                print('token: ' + str(token))
            else:
                print('missing token in data')

            if 'input' in data:
                print('input in data')

                if 'taskToken' in data:
                    print('Has task token')
                    taskToken = data['taskToken']
                    print('taskToken: '+str(taskToken))


                    print('Insert token into dynamodb')
                    dynamodb = boto3.resource('dynamodb')
                    table = dynamodb.Table(os.environ['TABLE_NAME'])

                    # Current time in seconds since epoch
                    current_time = int(time.time())

                    # Set the TTL attribute value (current time + number of seconds to live)
                    ttl_value = current_time + (int(1) * 7200)

                    # Prepare the item to be inserted
                    item = {
                        'token': taskToken,
                        'ttl': ttl_value
                    }

                    # Insert the item into the DynamoDB table
                    table.put_item(Item=item)

                    print('Item inserted successfully!')


                    body_data = json.loads(data['input']['body'])

                    values_to_check = [
                        "Vendor",
                        "Software",
                        "Requestor",
                        "Approver"
                    ]

                    all_values_present = True

                    for item in values_to_check:
                        print('item: '+str(item))
                        if item not in body_data:
                            all_values_present = False

                    if all_values_present:

                        if is_valid_email(os.environ['SENDER']):
                            print('email is valid')

                            print('All values present')
                            # SES client
                            ses_client = boto3.client('ses')

                            # Email parameters
                            SENDER = os.environ['SENDER']
                            RECIPIENT = body_data['Approver']
                            SUBJECT = "Amazon SES Test (AWS SDK for Python)"
                            BODY_TEXT = "This email was sent with Amazon SES using the AWS SDK for Python (Boto)."

                            # The email body for recipients with non-HTML email clients.

                            approve_api_url = os.environ['API_URL']+"/approve?authToken="+str(taskToken)+'&token='+str(token)
                            deny_api_url = os.environ['API_URL']+"/deny?authToken="+str(taskToken)+'&token='+str(token)


                            BODY_HTML = "<html><head></head><body><h1>Amazon SES Test</h1><p>This email was sent with<a href='xxx'>Amazon SES</a> using the<a href='https://boto3.amazonaws.com/v1/documentation/api/latest/index.html'>AWS SDK for Python (Boto)</a>.</p><p><a href='"+approve_api_url+"'>Approve</a></p><p><a href='"+deny_api_url+"'>Deny</a></p></body></html>"


                            print('body: '+str(BODY_HTML))

                            CHARSET = "UTF-8"

                            # Try to send the email.
                            try:
                                # Provide the contents of the email.
                                response = ses_client.send_email(
                                    Destination={
                                        'ToAddresses': [
                                            RECIPIENT,
                                        ],
                                    },
                                    Message={
                                        'Body': {
                                            'Html': {
                                                'Charset': CHARSET,
                                                'Data': BODY_HTML,
                                            },
                                            'Text': {
                                                'Charset': CHARSET,
                                                'Data': BODY_TEXT,
                                            },
                                        },
                                        'Subject': {
                                            'Charset': CHARSET,
                                            'Data': SUBJECT,
                                        },
                                    },
                                    Source=SENDER,
                                )
                            except ClientError as e:
                                print(e.response['Error']['Message'])
                            else:
                                print("Email sent! Message ID:"),
                                print(response['MessageId'])

                            return {
                                'statusCode': 200,
                                'body': json.dumps('Email sent successfully!')
                            }
                        else:
                            print('Missing required parameters4')
                            response = {
                                "statusCode": 200,
                                "headers": {
                                    "Content-Type": "application/json"
                                },
                                "body": json.dumps({"Message": "Email is invalid"})
                            }
                            return response
                else:
                    print('Missing required parameters4')
                    response = {
                        "statusCode": 200,
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": json.dumps({"Message": "Missing required parameters"})
                    }
                    return response
            else:
                print('Missing required parameters3')
                response = {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps({"Message": "Missing required parameters"})
                }
                return response
        else:
            print('Missing required parameters2')
            response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"Message": "Missing required parameters"})
            }
            return response

    else:
        print('Missing required parameters1')
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Message": "Missing required parameters"})
        }
        return response