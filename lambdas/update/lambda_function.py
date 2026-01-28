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
    UPDATE operation to MySQL database.
    Expected body: {"table": "items", "id": 1, "data": {"name": "new_value"}}
    """
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})

        table = body.get('table', 'items')
        record_id = body.get('id')
        data = body.get('data', {})

        if not record_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'ID is required'})
            }

        if not data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'No data provided for update'})
            }

        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(record_id)

        query = f"UPDATE {table} SET {set_clause} WHERE id = %s"

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
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
                'message': 'Record updated successfully',
                'affected_rows': affected_rows
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
