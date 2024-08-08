import json


def lambda_handler(event, context):
    print('event: '+str(event))
    print('context: '+str(context))

    # Process the request
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Processing sqs message",
            "input": "test"
        })
    }

    return response