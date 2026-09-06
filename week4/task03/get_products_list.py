import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')

    products_response = dynamodb.scan(
        TableName='cmtr-mxhmo8sx-dynamodb-l-table-products'
    )

    stocks_response = dynamodb.scan(
        TableName='cmtr-mxhmo8sx-dynamodb-l-table-stocks'
    )

    stocks = {}

    for stock in stocks_response.get('Items', []):
        stocks[stock['product_id']['S']] = stock

    result = None

    for product in products_response.get('Items', []):
        product_id = product['id']['S']

        if product_id.startswith(
            '14ba3d6a-a5ed-491b-a128-0a32b71a38c4-'
        ):
            merged = dict(product)

            if product_id in stocks:
                merged['count'] = stocks[product_id]['count']

            result = merged

    if result is None:
        return {
            'statusCode': 200,
            'body': json.dumps({})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }