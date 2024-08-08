import requests
import boto3
import pandas as pd
import json
import csv
from io import BytesIO
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
        # URL of the XLSX file
        xlsx_url = 'https://www.cisa.gov/sites/default/files/2024-07/July_2024_APL_7.26.24.xlsx'

        print('Fetch the XLSX file from the internet')
        response = requests.get(xlsx_url)
        response.raise_for_status()  # Check if the request was successful

        try:
            print('Read the XLSX file into a pandas DataFrame')
            xlsx_data = pd.read_excel(BytesIO(response.content), skiprows=[0, 1], sheet_name="Product List")

            print('Convert the DataFrame to a JSON object')
            json_data = xlsx_data.to_json(orient='records')

            try:
                flattened_data = flatten_json_array(json.loads(json_data))

                print('Convert flattened data to DataFrame')
                df = pd.DataFrame(flattened_data)

                print('Convert DataFrame to CSV in memory')
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False, header=False,quoting=csv.QUOTE_MINIMAL)

                try:
                    bucket_name = 'software-bucket-1234534452342'
                    # S3 key (path) where the file will be saved
                    s3_key = 'software.json'

                    print('Save the file to S3')
                    s3 = boto3.client('s3')
                    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue(),ContentType='text/csv')
                    return {
                        'statusCode': 200,
                        'body': 'File downloaded and saved to S3 successfully!'
                    }

                except Exception as e:

                    return {
                        'statusCode': 500,
                        'body': 'Failed to upload to S3.'+str(e)
                    }

            except Exception as e:

                return {
                    'statusCode': 500,
                    'body': 'Failed to flatten data.'+str(e)
                }

        except Exception as e:

            return {
                'statusCode': 500,
                'body': 'Failed to convert to data frame.'+str(e)
            }
    except Exception as e:

        return {
            'statusCode': 500,
            'body': 'Failed to download file.'+str(e)
        }

