import requests
import boto3
import pandas as pd
import csv
import json
from io import StringIO


def flatten_json(json_obj, parent_key='', sep='_'):
    items = []
    for k, v in json_obj.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def flatten_json_array(json_array):
    flattened_data = []
    for json_obj in json_array:
        flattened_data.append(flatten_json(json_obj))
    return flattened_data



def lambda_handler(event, context):

    try:
        print('event:'+str(event))
        print('context: '+str(context))
        # URL of the file to download
        file_url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'

        print('Download the file')
        response = requests.get(file_url)
        if response.status_code == 200:
            print('Parse the JSON content')
            json_data = response.json()

            try:
                print('Convert the JSON object to a string')
                flattened_data = flatten_json_array(json_data['vulnerabilities'])

                try:
                    print('Convert flattened data to DataFrame')
                    df = pd.DataFrame(flattened_data)

                    try:
                        print('Convert DataFrame to CSV in memory')
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False, header=False, quoting=csv.QUOTE_MINIMAL)

                        bucket_name = 'cve-bucket-1234534452342'
                        # S3 key (path) where the file will be saved
                        s3_key = 'cve.csv'

                        try:
                            # Save the file to S3
                            s3 = boto3.client('s3')
                            s3.put_object(Bucket=bucket_name, Key=s3_key,Body=csv_buffer.getvalue(),ContentType='text/csv')
                            #return {
                            #    'statusCode': 200,
                            #    'body': 'File downloaded and saved to S3 successfully!'
                            #}

                            response_body = {
                                "Software": str(event['Payload']['input']['Software']),
                                "Vendor": str(event['Payload']['input']['Vendor']),
                                "status": "success"
                            }
                            response = {
                                "statusCode": 200,
                                "headers": {
                                    "Content-Type": "application/json"
                                },
                                "body": json.dumps(response_body)
                            }
                            return response



                        except Exception as e:

                            return {
                                'statusCode': 500,
                                'body': 'Failed to upload to S3.'+str(e)
                            }

                    except Exception as e:

                        return {
                            'statusCode': 500,
                            'body': 'Failed to convert to csv.'+str(e)
                        }
                except Exception as e:

                    return {
                        'statusCode': 500,
                        'body': 'Failed to convert flatten data to data frame.'+str(e)
                    }
            except Exception as e:

                return {
                    'statusCode': 500,
                    'body': 'Failed to flatten data.'+str(e)
                }
        else:
            return {
                'statusCode': response.status_code,
                'body': 'Failed to download file.'
            }

    except Exception as e:

        return {
            'statusCode': 500,
            'body': 'Failed to download file.'+str(e)
        }

