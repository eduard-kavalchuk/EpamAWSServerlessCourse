import json
import requests
import uuid
import boto3
import os

from decimal import Decimal
from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


def get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["EVENTS_TABLE"])


class Processor(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        URL = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=52.52"
            "&longitude=13.41"
            "&current=temperature_2m,wind_speed_10m"
            "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )

        try:
            response = requests.get(URL, timeout=10)
            response.raise_for_status()
            forecast = response.json()

            ddb_forecast = json.loads(
                json.dumps(forecast),
                parse_float=Decimal
            )

            table = get_table()
            table.put_item(
                Item={
                    "id": str(uuid.uuid4()),
                    "forecast": ddb_forecast
                }
            )

            return {
                "statusCode": 200,
                "body": json.dumps(forecast)
            }

        except Exception as exc:
            print(exc)
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": str(exc)
                })
            }
    

HANDLER = Processor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
