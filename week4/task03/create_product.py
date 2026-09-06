import json
import boto3

def lambda_handler(event, context):
    uuid = '14ba3d6a-a5ed-491b-a128-0a32b71a38c4'

    if 'headers' in event and 'random-uuid' in event["headers"]:
        uuid += f'-{event["headers"]["random-uuid"]}'

    dynamodb = boto3.client('dynamodb')

    dynamodb.put_item(
        TableName='cmtr-mxhmo8sx-dynamodb-l-table-products',
        Item={
            'id': {'S': uuid},
            'title': {'S': 'Product Title'},
            'description': {'S': 'This product ...'},
            'price': {'N': '200'}
        }
    )

    dynamodb.put_item(
        TableName='cmtr-mxhmo8sx-dynamodb-l-table-stocks',
        Item={
            'product_id': {'S': uuid},
            'count': {'N': '2'}
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'id': uuid
        })
    }