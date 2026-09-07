import json

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

try:
    from weather_sdk import OpenMeteoClient
except ImportError:
    # For pytest only
    from lambdas.layers.weather_sdk.weather_sdk import OpenMeteoClient

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        path = (
            event.get("rawPath")
            or event.get("path")
            or ""
        )

        method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
            or event.get("httpMethod")
            or ""
        )

        if path != "/weather" or method != "GET":
            message = (
                f"Bad request syntax or unsupported method. "
                f"Request path: {path}. HTTP method: {method}"
            )

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "statusCode": 400,
                    "message": message
                })
            }

        try:
            client = OpenMeteoClient()
            weather = client.get_weather()

            return {
                "statusCode": 200,
                "body": json.dumps(weather)
            }

        except Exception as exc:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": str(exc)
                })
            }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
