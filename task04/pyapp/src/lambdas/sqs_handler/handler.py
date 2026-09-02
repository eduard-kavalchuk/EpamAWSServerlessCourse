import json

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)


class SqsHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        _LOG.info("Received event: %s", json.dumps(event))

        for record in event.get("Records", []):
            message_id = record.get("messageId")
            body = record.get("body")

            _LOG.info("Message ID: %s", message_id)
            _LOG.info("Message Body: %s", body)

        return {
            "statusCode": 200,
            "processedMessages": len(event.get("Records", []))
        }
    

HANDLER = SqsHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
