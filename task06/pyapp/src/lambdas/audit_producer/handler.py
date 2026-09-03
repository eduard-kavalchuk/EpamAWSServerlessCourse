import json
import uuid
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


def get_audit_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["AUDIT_TABLE"])

deserializer = TypeDeserializer()

def deserialize_image(image):
    """
    Converts DynamoDB stream format into a normal Python dict.
    """
    return {
        key: deserializer.deserialize(value)
        for key, value in image.items()
    }


def current_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def create_insert_audit(new_item):
    return {
        "id": str(uuid.uuid4()),
        "itemKey": new_item["key"],
        "modificationTime": current_timestamp(),
        "newValue": new_item
    }


def create_modify_audit(old_item, new_item):
    changes = []

    for attr in new_item:
        old_value = old_item.get(attr)
        new_value = new_item.get(attr)

        if old_value != new_value:
            changes.append({
                "id": str(uuid.uuid4()),
                "itemKey": new_item["key"],
                "modificationTime": current_timestamp(),
                "updatedAttribute": attr,
                "oldValue": old_value,
                "newValue": new_value
            })

    return changes


class AuditProducer(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        audit_table = get_audit_table()
    
        for record in event["Records"]:
            event_name = record["eventName"]

            if event_name == "INSERT":
                new_image = deserialize_image(
                    record["dynamodb"]["NewImage"]
                )

                audit_item = create_insert_audit(new_image)

                audit_table.put_item(
                    Item=audit_item
                )

            elif event_name == "MODIFY":
                old_image = deserialize_image(
                    record["dynamodb"]["OldImage"]
                )

                new_image = deserialize_image(
                    record["dynamodb"]["NewImage"]
                )

                audit_items = create_modify_audit(
                    old_image,
                    new_image
                )

                for audit_item in audit_items:
                    audit_table.put_item(
                        Item=audit_item
                    )

        return {
            "statusCode": 200
        }
    

HANDLER = AuditProducer()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
