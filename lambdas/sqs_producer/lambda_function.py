import json
import os
import boto3

sqs = boto3.client('sqs')

def lambda_handler(event, context):
    """
    SQS Producer - Sends create operation to SQS queue.
    Expected body: {"table": "items", "data": {"name": "value", "description": "value"}}
    """
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})

        table = body.get('table', 'items')
        data = body.get('data', {})

        if not data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No data provided'})
            }

        message = {
            'table': table,
            'data': data,
            'operation': 'create'
        }

        queue_url = os.environ['SQS_QUEUE_URL']

        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'Operation': {
                    'DataType': 'String',
                    'StringValue': 'create'
                }
            }
        )

        return {
            'statusCode': 202,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Create request queued successfully',
                'messageId': response['MessageId']
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
