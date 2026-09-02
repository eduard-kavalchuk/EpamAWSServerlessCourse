import json
import uuid
import boto3

from datetime import datetime, timezone

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


def get_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table("cmtr-mxhmo8sx-Events")


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        if "body" in event:
            request = json.loads(event["body"])
        else:
            request = event

        created_event = {
            "id": str(uuid.uuid4()),
            "principalId": request["principalId"],
            "createdAt": datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z"),
            "body": request["content"]
        }

        table = get_table()
        table.put_item(Item=created_event)

        return {
            "statusCode": 201,
            "event": created_event
        }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
