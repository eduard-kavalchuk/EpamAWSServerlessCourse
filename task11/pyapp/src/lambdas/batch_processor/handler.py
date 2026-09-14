from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import json

_LOG = get_logger(__name__)


class BatchProcessor(AbstractLambda):

    def validate_request(self, event):
        print("validate_request invoked")
        print(json.dumps(event))
        return None


    def handle_request(self, event, context):
        print("handle_request invoked")
        print(json.dumps(event))

        return {
            "statusCode": 200
        }
    

HANDLER = BatchProcessor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
