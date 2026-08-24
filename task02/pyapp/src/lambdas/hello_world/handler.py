from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class HelloWorld(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

    def handle_request(self, event, context):
        """
        Lambda function that handles GET requests via Function URL.
        Returns different responses based on the request path.
        """

        # Extract path and method from the event
        # For Function URLs, the raw path is in event['rawPath']
        path = event.get('rawPath', '/')
        method = event.get('requestContext', {}).get("http", {}).get('method', 'GET')

        if path == '/hello' and method == 'GET':
            return {'statusCode': 200, 'message': 'Hello from Lambda'}
        else:
            return {
                'statusCode': 400,
                'message': f'Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}'
            }


HANDLER = HelloWorld()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
