from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

from commons.db import execute
import os
import json

_LOG = get_logger(__name__)


INIT_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_type
        WHERE typname = 'statustype'
    ) THEN
        CREATE TYPE StatusType AS ENUM (
            'CREATED',
            'IN_TRANSIT',
            'DELAYED',
            'DELIVERED',
            'CANCELLED'
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50),
    origin VARCHAR(100),
    destination VARCHAR(100),
    weight_kg DECIMAL(10,2),
    created_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS carriers (
    carrier_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN
);

CREATE TABLE IF NOT EXISTS status_updates (
    update_id SERIAL PRIMARY KEY,
    shipment_id VARCHAR(50)
        REFERENCES shipments(shipment_id),
    carrier_id VARCHAR(50)
        REFERENCES carriers(carrier_id),
    status StatusType,
    location VARCHAR(100),
    notes TEXT,
    timestamp TIMESTAMPTZ
);
"""


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        print("validate_request invoked")
        return None


    def handle_request(self, event, context):
        # return {
        #     "statusCode": 200,
        #     "body": json.dumps(dict(os.environ))
        # }

        print(dict(os.environ))
    
        if (
            event.get("resource") == "/initdb"
            and event.get("httpMethod") == "POST"
        ):
            execute(INIT_SQL)

            return {
                "statusCode": 200,
                "body": "Database initialized"
            }

        return {
            "statusCode": 404,
            "body": "Not found"
        }

    
HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
