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
    DELETE operation from MySQL database.
    Expected body: {"table": "items", "id": 1}
    """
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        params = event.get('queryStringParameters', {}) or {}

        table = body.get('table') or params.get('table', 'items')
        record_id = body.get('id') or params.get('id')

        if not record_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'ID is required'})
            }

        query = f"DELETE FROM {table} WHERE id = %s"

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
                affected_rows = cursor.rowcount
            connection.commit()
        finally:
            connection.close()

        if affected_rows == 0:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Record not found'})
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Record deleted successfully',
                'affected_rows': affected_rows
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
