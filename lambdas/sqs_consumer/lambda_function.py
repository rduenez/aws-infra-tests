import json
import os
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def lambda_handler(event, context):
    """
    SQS Consumer - Processes messages from SQS queue and writes to database.
    Triggered by SQS events.
    """
    processed = 0
    failed = 0

    for record in event.get('Records', []):
        try:
            message = json.loads(record['body'])

            table = message.get('table', 'items')
            data = message.get('data', {})

            if not data:
                print(f"Skipping message with no data: {record['messageId']}")
                failed += 1
                continue

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            connection = get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, values)
                    inserted_id = cursor.lastrowid
                connection.commit()
                print(f"Successfully inserted record with ID: {inserted_id}")
                processed += 1
            finally:
                connection.close()

        except Exception as e:
            print(f"Error processing message {record.get('messageId', 'unknown')}: {str(e)}")
            failed += 1
            raise  # Re-raise to trigger retry/DLQ

    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': processed,
            'failed': failed
        })
    }
