import json
import os
import pymysql
from decimal import Decimal

def get_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    """
    READ operation from MySQL database.
    Query params: table (required), id (optional for single record)
    """
    try:
        # Get parameters from query string or body
        params = event.get('queryStringParameters', {}) or {}
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})

        table = params.get('table') or body.get('table', 'items')
        record_id = params.get('id') or body.get('id')

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                if record_id:
                    query = f"SELECT * FROM {table} WHERE id = %s"
                    cursor.execute(query, (record_id,))
                    result = cursor.fetchone()
                else:
                    query = f"SELECT * FROM {table} LIMIT 100"
                    cursor.execute(query)
                    result = cursor.fetchall()
        finally:
            connection.close()

        if result is None:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Record not found'})
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'data': result}, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
