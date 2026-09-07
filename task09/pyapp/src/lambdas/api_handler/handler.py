import json

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

try:
    from weather_sdk import OpenMeteoClient
except ImportError:
    from lambdas.layers.weather_sdk.weather_sdk import OpenMeteoClient

_LOG = get_logger(__name__)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        print(f"Received event: {json.dumps(event)}")

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

        print(f"Request path: {path}")
        print(f"Request method: {method}")

        if path != "/weather" or method != "GET":
            message = (
                f"Bad request syntax or unsupported method. "
                f"Request path: {path}. HTTP method: {method}"
            )

            print(message)

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "statusCode": 400,
                    "message": message
                })
            }

            # return {
            #     "statusCode": 400,
            #     "message": message
            # }

        try:
            print("Creating OpenMeteoClient")

            client = OpenMeteoClient()

            print("Requesting weather forecast")

            weather = client.get_weather()

            print("Forecast successfully retrieved")

            return {
                "statusCode": 200,
                "body": json.dumps(weather)
            }

            

        except Exception as exc:
            print(f"Weather request failed: {str(exc)}")

            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": str(exc)
                })
            }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
