import json
import boto3
import os
from boto3.dynamodb.conditions import Key



# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

# Custom authorizer for api gateway
def lambda_handler(event, context):
    print("event: " + str(event))
    print("context:" + str(context))

    if 'queryStringParameters' in event:
        print('has query string parameter')

        if 'authToken' in event['queryStringParameters']:
            print('has auth token')
            token = event['queryStringParameters']['authToken']
            print('token: '+str(token))

            # Lookup the API key in DynamoDB
            try:

                response = table.query(
                    KeyConditionExpression=Key('token').eq(token)
                )

                print('response: '+str(response))

                if 'Items' in response:
                    print('item in response')
                    return {
                        'principalId': 'user',
                        'policyDocument': {
                            'Version': '2012-10-17',
                            'Statement': [
                                {
                                    'Action': 'execute-api:Invoke',
                                    'Effect': 'Allow',
                                    'Resource': event['methodArn']
                                }
                            ]
                        }
                    }
                else:
                    print('no item in response')
                    return {
                        'principalId': 'user',
                        'policyDocument': {
                            'Version': '2012-10-17',
                            'Statement': [
                                {
                                    'Action': 'execute-api:Invoke',
                                    'Effect': 'Deny',
                                    'Resource': event['methodArn']
                                }
                            ]
                        }
                    }


            except Exception as e:
                print(e)
                return {
                    'principalId': 'user',
                    'policyDocument': {
                        'Version': '2012-10-17',
                        'Statement': [
                            {
                                'Action': 'execute-api:Invoke',
                                'Effect': 'Deny',
                                'Resource': event['methodArn']
                            }
                        ]
                    }
                }

    else:
        return {
            'principalId': 'user',
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Deny',
                        'Resource': event['methodArn']
                    }
                ]
            }
        }

