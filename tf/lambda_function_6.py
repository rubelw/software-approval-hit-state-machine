import json
import boto3
import time
import datetime
import os
import secrets
import inspect
import re
import mysql.connector

def lineno():
    """
    Print line number
    """
    return str('  - line number: ' +
               str(inspect.currentframe().f_back.f_lineno))  # pragma: no cover



def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


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
        if event['path'] == '/clear':
            connection = mysql.connector.connect(
                host=os.environ['DB_HOST'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD'],
                database=os.environ['DB_NAME']
            )

            cursor = connection.cursor()
            select_query = "DELETE FROM requested_approval"
            print('query: ' + str(select_query) + lineno())
            cursor.execute(select_query)
            connection.commit()

            select_query = "DELETE FROM approved_software"
            print('query: ' + str(select_query) + lineno())
            cursor.execute(select_query)
            connection.commit()

            response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"Message": "Databases cleaned-up"})
            }
            return response

        if event['path'] == '/approve':

            if 'queryStringParameters' in event:
                print('has query string parameter')

                if 'authToken' in event['queryStringParameters']:
                    print('has auth token')
                    token = event['queryStringParameters']['authToken']
                    print('token: ' + str(token))


                    try:
                        print('Trying to query request table'+lineno())

                        connection = mysql.connector.connect(
                            host=os.environ['DB_HOST'],
                            user=os.environ['DB_USER'],
                            password=os.environ['DB_PASSWORD'],
                            database=os.environ['DB_NAME']
                        )

                        cursor = connection.cursor()

                        select_query = "SELECT * FROM requested_approval WHERE token ='" + str(token)+"'"

                        print('query: '+str(select_query)+lineno())

                        cursor.execute(select_query)

                        # Fetch all rows as dictionaries
                        results = cursor.fetchall()

                        # results: [(4, 'mr6mmYLfplhmKy8F2ltJ_0JCSB8pDmWXE_7lPXHjoag', 'CVE-2020-11978',
                        # 'Apache', 'airflow', 'willrubel@gmail.com', 'willrubel@gmail.com',
                        # datetime.datetime(2024, 8, 14, 10, 8, 32, 608436)),
                        # (5, 'mr6mmYLfplhmKy8F2ltJ_0JCSB8pDmWXE_7lPXHjoag', 'CVE-2020-13927', 'Apache',
                        # 'airflow', 'willrubel@gmail.com', 'willrubel@gmail.com', datetime.datetime(2024, 8, 14, 10, 8, 32, 628620))]
                        print('results: ' + str(results) + lineno())

                        cursor.close()

                        if len(results)>0:
                            print('item in response: '+lineno())

                            for item in results:
                                print('item: '+str(item)+lineno())

                                cursor = connection.cursor()

                                select_query = "SELECT * FROM approved_software WHERE cve ='" + str(item[2])+"'"

                                cursor.execute(select_query)

                                # Fetch all rows as dictionaries
                                approved_results = cursor.fetchall()
                                print('approved results: ' + str(approved_results) + lineno())


                                if len(approved_results)<1:
                                    print("No approved results"+lineno())

                                    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                                    print('Prepare the item to be inserted' + lineno())
                                    print('cve: ' + str(item[2]) + lineno())
                                    print('vendor: ' + str(item[3]))
                                    print('software: '+str(item[4])+lineno())
                                    print('requestor: ' + str(item[5]))
                                    print('approver: '+str(item[6])+lineno())


                                    cursor2 = connection.cursor()

                                    # CREATE TABLE approved_software (id INT AUTO_INCREMENT PRIMARY KEY,
                                    # cve VARCHAR(50) NOT NULL,vendor VARCHAR(50) NOT NULL,
                                    # software VARCHAR(100),requestor VARCHAR(100),
                                    # approver VARCHAR(100),approved_at DATETIME(6) NOT NULL);

                                    insert_query = "INSERT INTO approved_software (cve, vendor, software, requestor, approver,approved_at) VALUES ('" + str(
                                        item[2]) + "','" + str(item[3]) + "','" + str(
                                        item[4]) + "','" + str(item[5]) + "','" + str(
                                        item[6]) + "','" + str(current_datetime) + "')"

                                    print('insert query: ' + str(insert_query) + lineno())
                                    cursor2.execute(insert_query)
                                    connection.commit()
                                    cursor2.close()

                                    print('Insert the item into the table' + lineno())



                                else:
                                    print('Already approved'+lineno())



                            response = {
                                "statusCode": 200,
                                "headers": {
                                    "Content-Type": "application/json"
                                },
                                "body": json.dumps({"Message": "Approved"})
                            }
                            return response

                        else:
                            print('Token not in requested table' + lineno())
                            response = {
                                "statusCode": 500,
                                "headers": {
                                    "Content-Type": "application/json"
                                },
                                "body": json.dumps({"Message": "Problem with token"})
                            }
                            return response

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

                else:
                    return {
                        'statusCode': 400,
                        'body': 'Missing  token'
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
            if 'queryStringParameters' in event:
                print('has query string parameter')

                if 'authToken' in event['queryStringParameters']:
                    print('has auth token')
                    token = event['queryStringParameters']['authToken']
                    print('token: ' + str(token))

                    try:
                        print('Trying to query request table' + lineno())

                        connection = mysql.connector.connect(
                            host=os.environ['DB_HOST'],
                            user=os.environ['DB_USER'],
                            password=os.environ['DB_PASSWORD'],
                            database=os.environ['DB_NAME']
                        )

                        cursor = connection.cursor()

                        select_query = "DELETE FROM requested_approval WHERE token ='" + str(token) + "'"

                        print('query: ' + str(select_query) + lineno())

                        cursor.execute(select_query)



                        response = {
                            "statusCode": 500,
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "body": json.dumps({"Message": "Has deny"})
                        }
                        return response

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
                else:
                    response = {
                        "statusCode": 500,
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": json.dumps({"Message": "No auth token found"})
                    }
                    return response
            else:
                response = {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps({"Message": "No query parameter found"})
                }
                return response


        else:
            if 'body' in event:
                data = json.loads(event['body'])
                print('data: ' + str(data)+lineno())

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

                    print('Initialize Athena client'+lineno())
                    client = boto3.client('athena')

                    # Define query parameters
                    database = 'cve-database'
                    workgroup = "example-workgroup"


                    # SELECT cvdid, product,vulnerabilityname FROM cve_table where LOWER(product) LIKE LOWER('%airflow%')
                    # SELECT cvdid, product,vulnerabilityname,vendorproject FROM cve_table where LOWER(vendorproject) LIKE LOWER('%apache%')

                    query = 'SELECT cvdid, product, vulnerabilityname FROM cve_table where LOWER(vendorproject) LIKE LOWER(\'%'+str(data['Vendor'])+'%\') and LOWER(product) LIKE LOWER(\'%'+str(data['Software'])+'%\')'  # Your SQL query
                    output_location = 's3://output-bucket-1234534452342/'

                    print('query string: '+str(query)+lineno())
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
                    print('response: '+str(response)+lineno())
                    print('query id: '+str(query_execution_id)+lineno())
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
                        print('row: '+str(row)+lineno())
                        if row['Data'][0]['VarCharValue'] == 'cvid':
                            continue

                        temp_hash = {}
                        temp_hash['cve'] = row['Data'][0]['VarCharValue']
                        temp_hash['vendor'] = row['Data'][1]['VarCharValue']
                        temp_hash['software'] = row['Data'][2]['VarCharValue']

                        rows.append(temp_hash)

                    dynamodb = boto3.resource('dynamodb')
                    # Initialize the DynamoDB client
                    table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
                    token = generate_urlsafe_token(32)

                    # Current time in seconds since epoch
                    current_time = int(time.time())

                    # Set the TTL attribute value (current time + number of seconds to live)
                    ttl_value = current_time + (int(1) * 7776000)

                    # Set the TTL attribute value (current time + number of seconds to live)
                    ttl_value = current_time  # 90 days

                    item = {
                        'token': token,
                        'ttl': ttl_value
                    }

                    print('Insert the item into the table'+lineno())
                    table.put_item(Item=item)

                    connection = mysql.connector.connect(
                        host=os.environ['DB_HOST'],
                        user=os.environ['DB_USER'],
                        password=os.environ['DB_PASSWORD'],
                        database=os.environ['DB_NAME']
                    )

                    cursor = connection.cursor()

                    insert_query = "INSERT INTO requested_tokens (token) VALUES (%(token)s)"
                    newdata = {
                        'token': str(token)
                    }

                    cursor.execute(insert_query, newdata)
                    connection.commit()

                    print('inserted token into requested_tokens'+lineno())

                    unapproved_cves= []
                    if len(rows)>0:
                        print('has rows'+lineno())
                        try:
                            counter = 0
                            for row in rows:
                                if counter < 1:  # Skip the header row
                                    counter = counter + 1
                                    continue

                                select_query = "SELECT * FROM approved_software  WHERE cve='"+str(row['cve'])+"'"
                                print('select query: '+str(select_query)+lineno())
                                cursor2 = connection.cursor()

                                cursor2.execute(select_query)

                                # Fetch all rows as dictionaries
                                results = cursor2.fetchall()
                                print('results: '+str(results)+lineno())

                                if len(results)>0:
                                    print('has approved software - not doing anything'+lineno())

                                else:
                                    print('no item in approved software'+lineno())
                                    # Current time in seconds since epoch
                                    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                                    print('Prepare the item to be inserted' + lineno())
                                    print('cve: ' + str(row['cve']) + lineno())
                                    print('vendor: ' + str(data['Vendor']))
                                    print('software: '+str(data['Software'])+lineno())
                                    print('requestor: ' + str(data['Requestor']))
                                    print('approver: '+str(data['Approver'])+lineno())

                                    # CREATE TABLE requested_approval (id INT AUTO_INCREMENT PRIMARY KEY,
                                    # token VARCHAR(50) NOT NULL,
                                    # cve VARCHAR(50) NOT NULL,
                                    # vendor VARCHAR(50) NOT NULL,
                                    # software VARCHAR(100),
                                    # requestor VARCHAR(100),
                                    # approver VARCHAR(100),
                                    # requested_date DATE NOT NULL,FOREIGN KEY (token) REFERENCES requested_tokens(token) ON DELETE CASCADE);

                                    cursor2 = connection.cursor()

                                    insert_query = "INSERT INTO requested_approval (token, cve, vendor, software, approver, requestor,requested_at) VALUES ('" + str(token) + "','" + str(row['cve']) + "','"  + str(data['Vendor']) + "','" + str(data['Software']) + "','" + str(data['Approver']) + "','" + str(data['Requestor']) + "','" + str(current_datetime)+"')"

                                    print('insert query: '+str(insert_query)+lineno())
                                    cursor2.execute(insert_query, data)
                                    connection.commit()
                                    cursor2.close()

                                    print('Insert the item into the table' + lineno())
                                    print('item: ' + str(item) + lineno())
                                    print('row: ' + str(row) + lineno())

                                    unapproved_cves.append(row['cve'])

                        except Exception as e:

                            print('Exception: '+str(e))
                            connection.close()

                            response = {
                                "statusCode": 500,
                                "headers": {
                                    "Content-Type": "application/json"
                                },
                                "body": json.dumps({"Message": "Problem with dynamodb"})
                            }
                            return response


                    if len(unapproved_cves)>0:
                        print('unapproved cves: '+str(unapproved_cves)+lineno())

                        print('Insert token into dynamodb')
                        dynamodb = boto3.resource('dynamodb')
                        table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

                        # Current time in seconds since epoch
                        current_time = int(time.time())

                        # Set the TTL attribute value (current time + number of seconds to live)
                        ttl_value = current_time + (int(1) * 7200)

                        # Prepare the item to be inserted
                        item = {
                            'token': token,
                            'ttl': ttl_value
                        }

                        # Insert the item into the DynamoDB table
                        table.put_item(Item=item)

                        print('Item inserted successfully!')

                        if is_valid_email(os.environ['SENDER']):
                            print('email is valid')

                            print('All values present')
                            # SES client
                            ses_client = boto3.client('ses')

                            print('data: '+str(data))
                            # Email parameters
                            SENDER = os.environ['SENDER']
                            RECIPIENT = data['Approver']
                            SUBJECT = "Software approval request for "+str(data['Software'])
                            BODY_TEXT = "This email was sent with Amazon SES using the AWS SDK for Python (Boto)."

                            # The email body for recipients with non-HTML email clients.

                            approve_api_url = os.environ['API_URL'] + "/approve?authToken=" + str(token)
                            deny_api_url = os.environ['API_URL'] + "/deny?authToken=" + str(token)

                            # Convert list to HTML unordered list
                            html_content = "<ul>\n"
                            for item in unapproved_cves:
                                html_content += f"    <li>https://nvd.nist.gov/vuln/detail/{item}</li>\n"
                            html_content += "</ul>"


                            BODY_HTML = f"""
                            <html>
                            <head></head>
                            <body>
                            <h1>Approved Software Test</h1>
                            {html_content}
                            <p>Requestor: {data['Requestor']} has requested approval of the following CVEs. Please review and select 'Approve' or 'Deny'.</p>
                            <p><a href="{approve_api_url}">Approve</a></p>
                            <p><a href="{deny_api_url}">Deny</a></p>
                            </body>
                            </html>"""

                            print('body: ' + str(BODY_HTML)+lineno())

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
                        response = {
                            "statusCode": 500,
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "body": json.dumps({"Message": "No un-approved software found"})
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