import json
import uuid
import boto3
import os

from datetime import datetime, timezone

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)

def get_tables_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["TABLES_TABLE"])

def get_reservations_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["RESERVATIONS_TABLE"])


def get_pool_name():
    return os.environ["USER_POOL_NAME"]


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        return {
            "statusCode": 200,
            "body": json.dumps({
                "resource": event.get("resource"),
                "path": event.get("path"),
                "httpMethod": event.get("httpMethod")
            })
        }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
