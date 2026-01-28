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
    Direct CREATE operation to MySQL database.
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
        finally:
            connection.close()

        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Record created successfully',
                'id': inserted_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
