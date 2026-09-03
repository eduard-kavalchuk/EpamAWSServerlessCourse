from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import json
import uuid
import os
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")

_LOG = get_logger(__name__)


class UuidGenerator(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        execution_time = datetime.now(timezone.utc)

        uuids = [str(uuid.uuid4()) for _ in range(10)]

        payload = {
            "ids": uuids
        }

        object_key = execution_time.isoformat(timespec="milliseconds")
        object_key = object_key.replace("+00:00", "Z")

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=json.dumps(payload),
            ContentType="application/json"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "file": object_key,
                    "count": 10
                }
            )
        }
    

HANDLER = UuidGenerator()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
