import json
import boto3
import time
import os
import secrets
from boto3.dynamodb.conditions import Key


stepfunctions = boto3.client('stepfunctions')


def generate_urlsafe_token(length=32):
    return secrets.token_urlsafe(length)

def update_dynamodb_table(token, update_expression, expression_attribute_values):
    try:
        # Update dynamodb approved cves
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_APPROVED_TABLE_NAME'])


        response = table.update_item(
            TableName=os.environ['DYNAMODB_APPROVED_TABLE_NAME'],
            Key={"token": token },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        print(f"Error updating item: {e}")
        return None

# Handles all API gateway request
def lambda_handler(event, context):
    print('event: '+str(event))
    print('context: '+str(context))


    if 'path' in event:
        if event['path'] == '/approve':

            if 'queryStringParameters' in event:
                print('has query string parameter')

                if 'authToken' in event['queryStringParameters']:
                    print('has auth token')
                    token = event['queryStringParameters']['authToken']
                    print('token: ' + str(token))
                    approval_token = event['queryStringParameters']['token']
                    print('approval token: '+str(approval_token))

                    try:
                        print('Trying to query dynamodb')

                        dynamodb = boto3.resource('dynamodb')
                        table = dynamodb.Table(os.environ['DYNAMODB_APPROVED_TABLE_NAME'])

                        response = table.query(
                            IndexName='TokenIndex',
                            KeyConditionExpression=Key('token').eq(approval_token)
                        )

                        print('response: ' + str(response))

                        if 'Items' in response:
                            print('item in response')

                            # Current time in seconds since epoch
                            current_time = int(time.time())

                            # Set the TTL attribute value (current time + number of seconds to live)
                            ttl_value = current_time + (int(1) * 7776000)

                            # Set the TTL attribute value (current time + number of seconds to live)
                            ttl_value = current_time  # 90 days

                            # Define the primary key of the item to update
                            key = {
                                "token": {"S": str(token)}
                            }

                            # Define the update expression
                            update_expression = "SET status = :status"

                            # Define the expression attribute values
                            expression_attribute_values = {
                                ":status": "approved"
                            }

                            update_dynamodb_table(token, update_expression, expression_attribute_values)

                    except Exception as e:
                        print(e)

                        response = {
                            "statusCode": 500,
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "body": json.dumps({"Message": "Problem with dynamodb"})
                        }
                        return response

                    # Prepare the output data
                    output_data = {
                        'status': 'success',
                        'message': 'Task completed successfully',
                        'result': {
                            # Add any results or output you want to pass back to the Step Function
                        }
                    }

                    try:
                        response = stepfunctions.send_task_success(
                            taskToken=token,
                            output=json.dumps(output_data)
                        )
                    except Exception as e:
                        print(f"Error completing task: {e}")
                        response = stepfunctions.send_task_failure(
                            taskToken=token,
                            error='TaskFailure',
                            cause=str(e)
                        )

                else:
                    return {
                        'statusCode': 400,
                        'body': 'Missing task token'
                    }


            response = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"Message": "Has approve"})
            }
            return response

        elif event['path'] == '/deny':
            response = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"Message": "Has deny"})
            }
            return response
        else:


            if 'body' in event:
                data = json.loads(event['body'])
                print('data: ' + str(data))

                values_to_check = [
                    "Vendor",
                    "Software",
                    "Requestor",
                    "Approver"
                ]

                all_values_present = True

                for item in values_to_check:
                    if item not in data:
                        all_values_present = False

                if all_values_present:

                    print('Initialize Athena client')
                    client = boto3.client('athena')

                    # Define query parameters
                    database = 'cve-database'
                    workgroup = "example-workgroup"


                    # SELECT cvdid, product,vulnerabilityname FROM cve_table where LOWER(product) LIKE LOWER('%airflow%')
                    # SELECT cvdid, product,vulnerabilityname,vendorproject FROM cve_table where LOWER(vendorproject) LIKE LOWER('%apache%')

                    query = 'SELECT cvdid, product, vulnerabilityname FROM cve_table where LOWER(vendorproject) LIKE LOWER(\'%'+str(data['Vendor'])+'%\') and LOWER(product) LIKE LOWER(\'%'+str(data['Software'])+'%\')'  # Your SQL query
                    output_location = 's3://output-bucket-1234534452342/'

                    # Start query execution
                    response = client.start_query_execution(
                        QueryString=query,
                        WorkGroup=workgroup,
                        QueryExecutionContext={
                            'Database': database
                        },
                        ResultConfiguration={
                            'OutputLocation': output_location
                        }
                    )

                    query_execution_id = response['QueryExecutionId']
                    print('response: '+str(response))
                    print('query id: '+str(query_execution_id))
                    # Poll for query completion
                    while True:
                        response = client.get_query_execution(QueryExecutionId=query_execution_id)
                        status = response['QueryExecution']['Status']['State']

                        if status == 'SUCCEEDED':
                            break
                        elif status in ['FAILED', 'CANCELLED']:
                            raise Exception(f"Query failed with status: {status}")

                        time.sleep(2)  # Wait before polling again

                    # Retrieve query results
                    results = client.get_query_results(QueryExecutionId=query_execution_id)

                    # Extract and format results
                    rows = []
                    for row in results['ResultSet']['Rows']:
                        print('row: '+str(row))

                        temp_hash = {}
                        temp_hash['cve'] = row['Data'][0]['VarCharValue']
                        temp_hash['vendor'] = row['Data'][1]['VarCharValue']
                        temp_hash['software'] = row['Data'][2]['VarCharValue']

                        rows.append(temp_hash)

                    print('Add rows to approved cves table')

                    # Initialize the DynamoDB client
                    dynamodb = boto3.resource('dynamodb')
                    table = dynamodb.Table(os.environ['DYNAMODB_APPROVED_TABLE_NAME'])

                    unapproved_rows = []
                    token = generate_urlsafe_token(32)

                    try:

                        counter = 0
                        for row in rows:
                            if counter <1:  # Skip the header row
                                counter=counter+1
                                continue

                            response = table.query(
                                KeyConditionExpression=Key('cve').eq(row['cve'])
                            )

                            print('response: ' + str(response))

                            if 'Items' in response:
                                print('item in response')

                                # Current time in seconds since epoch
                                current_time = int(time.time())

                                # Set the TTL attribute value (current time + number of seconds to live)
                                ttl_value = current_time + (int(1) * 7776000)

                                # Set the TTL attribute value (current time + number of seconds to live)
                                ttl_value = current_time  # 90 days

                                print('Prepare the item to be inserted')
                                print('cve: '+str(row['cve']))
                                print('vendor: '+str(data['Vendor']))
                                print('requestor: '+str(data['Requestor']))

                                item = {
                                    'token': token,
                                    'cve': row['cve'],
                                    'vendor': data['Vendor'],
                                    'software': data['Software'],
                                    'requestor': data['Requestor'],
                                    'approver': data['Approver'],
                                    'status': 'pending',
                                    'ttl': ttl_value
                                }

                                print('Insert the item into the DynamoDB table')
                                table.put_item(Item=item)

                            else:
                                print('no item in response')

                                unapproved_rows.append[row]

                    except Exception as e:

                        print(e)

                        response = {
                            "statusCode": 500,
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "body": json.dumps({"Message": "Problem with dynamodb"})
                        }
                        return response

                    if len(results['ResultSet']['Rows'])<2:
                        print('Has less than 2 rows')
                        # Fetch the ARN of the second Lambda function from environment variables
                        second_lambda_arn = os.environ['SECOND_LAMBDA_ARN']


                        print('Invoke the second Lambda function')
                        response = client.invoke(
                            FunctionName=second_lambda_arn,
                            InvocationType='Event',  # Use 'RequestResponse' for synchronous invocation
                            Payload=json.dumps({'cves': rows, 'requestor': data['Requestor'],'approver':data['Approver']})
                        )

                        return {
                            'statusCode': 200,
                            'body': json.dumps('Lambda 2 invoked successfully'),
                            'response': response
                        }
                    else:

                        #row: {'Data': [{'VarCharValue': 'CVE-2020-11978'}, {'VarCharValue': 'Airflow'},
                        #               {'VarCharValue': 'Apache Airflow Command Injection'}]}

                        print('starting step function')
                        client = boto3.client('stepfunctions')

                        # Fetch the State Machine ARN from environment variables
                        state_machine_arn = os.environ['STATE_MACHINE_ARN']

                        event['token'] = token
                        # Start State Machine execution
                        response = client.start_execution(
                            stateMachineArn=state_machine_arn,
                            name = token,
                            input=json.dumps(event)  # Pass the event as input to the state machine
                        )

                        return {
                            'statusCode': 200,
                            'body': json.dumps('State machine execution started successfully'),
                            'executionArn': response['executionArn']
                        }

                else:
                    response = {
                        "statusCode": 500,
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": json.dumps({"Message": "Missing requirement parameters"})
                    }
                    return response
            else:
                response = {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps({"Message": "Missing requirement parameters"})
                }
                return response

    else:
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"Message": "Bad path"})
        }
        return response