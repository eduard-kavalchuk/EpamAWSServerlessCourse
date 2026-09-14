from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import json

from commons.mappers import (
    row_to_shipment,
    row_to_carrier,
    row_to_status_update
)

from commons.db import (
    execute,
    fetch_one,
    fetch_all,
    execute_returning
)

VALID_STATUSES = {
    "CREATED",
    "IN_TRANSIT",
    "DELAYED",
    "DELIVERED",
    "CANCELLED"
}


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

CREATE_SHIPMENT_SQL = """
INSERT INTO shipments (
    shipment_id,
    order_id,
    origin,
    destination,
    weight_kg,
    created_at
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    NOW()
)
RETURNING
    shipment_id,
    order_id,
    origin,
    destination,
    weight_kg,
    created_at
"""

CREATE_CARRIER_SQL = """
INSERT INTO carriers (
    carrier_id,
    name,
    email,
    phone,
    is_active
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s
)
RETURNING
    carrier_id,
    name,
    email,
    phone,
    is_active
"""

GET_SHIPMENT_SQL = """
SELECT
    shipment_id,
    order_id,
    origin,
    destination,
    weight_kg,
    created_at
FROM shipments
WHERE shipment_id = %s
"""

GET_CARRIER_SQL = """
SELECT
    carrier_id,
    name,
    email,
    phone,
    is_active
FROM carriers
WHERE carrier_id = %s
"""

UPDATE_CARRIER_SQL = """
UPDATE carriers
SET
    name = %s,
    email = %s,
    phone = %s,
    is_active = %s
WHERE carrier_id = %s
RETURNING
    carrier_id,
    name,
    email,
    phone,
    is_active
"""

DELETE_CARRIER_SQL = """
DELETE FROM carriers
WHERE carrier_id = %s
RETURNING
    carrier_id,
    name,
    email,
    phone,
    is_active
"""

UPDATE_SHIPMENT_SQL = """
UPDATE shipments
SET
    order_id = %s,
    origin = %s,
    destination = %s,
    weight_kg = %s
WHERE shipment_id = %s
RETURNING
    shipment_id,
    order_id,
    origin,
    destination,
    weight_kg,
    created_at
"""

DELETE_SHIPMENT_SQL = """
DELETE FROM shipments
WHERE shipment_id = %s
RETURNING
    shipment_id,
    order_id,
    origin,
    destination,
    weight_kg,
    created_at
"""

CREATE_STATUS_UPDATE_SQL = """
INSERT INTO status_updates (
    shipment_id,
    carrier_id,
    status,
    location,
    notes,
    timestamp
)
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    NOW()
)
RETURNING
    update_id,
    shipment_id,
    carrier_id,
    status,
    location,
    notes,
    timestamp
"""

GET_STATUS_UPDATES_SQL = """
SELECT
    update_id,
    shipment_id,
    carrier_id,
    status,
    location,
    notes,
    timestamp
FROM status_updates
WHERE shipment_id = %s
ORDER BY timestamp
"""




class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        return None


    def handle_request(self, event, context):
        if (
            event.get("resource") == "/initdb"
            and event.get("httpMethod") == "POST"
        ):
            execute(INIT_SQL)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Database initialized"
                })
            }

        elif (
            event.get("resource") == "/shipments"
            and event.get("httpMethod") == "POST"
        ):
            body = json.loads(event["body"])

            existing = fetch_one(
                """
                SELECT shipment_id
                FROM shipments
                WHERE shipment_id = %s
                """,
                (body["shipment_id"],)
            )

            if existing:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Shipment already exists"
                    })
                }

            row = execute_returning(
                CREATE_SHIPMENT_SQL,
                (
                    body["shipment_id"],
                    body["order_id"],
                    body["origin"],
                    body["destination"],
                    body["weight_kg"]
                )
            )

            return {
                "statusCode": 201,
                "body": json.dumps(
                    row_to_shipment(row)
                )
            }

        elif (
            event.get("resource") == "/carriers"
            and event.get("httpMethod") == "POST"
        ):
            body = json.loads(event["body"])

            existing = fetch_one(
                """
                SELECT carrier_id
                FROM carriers
                WHERE carrier_id = %s
                """,
                (body["carrier_id"],)
            )

            if existing:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Carrier already exists"
                    })
                }

            row = execute_returning(
                CREATE_CARRIER_SQL,
                (
                    body["carrier_id"],
                    body["name"],
                    body["email"],
                    body["phone"],
                    body["is_active"]
                )
            )

            return {
                "statusCode": 201,
                "body": json.dumps(
                    row_to_carrier(row)
                )
            }

        elif (
            event.get("resource") == "/shipments/{shipmentId}"
            and event.get("httpMethod") == "GET"
        ):

            shipment_id = (
                event["pathParameters"]["shipmentId"]
            )

            row = fetch_one(
                GET_SHIPMENT_SQL,
                (shipment_id,)
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Shipment not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_shipment(row)
                )
            }

        elif (
            event.get("resource") == "/carriers/{carrierId}"
            and event.get("httpMethod") == "GET"
        ):

            carrier_id = (
                event["pathParameters"]["carrierId"]
            )

            row = fetch_one(
                GET_CARRIER_SQL,
                (carrier_id,)
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Carrier not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_carrier(row)
                )
            }

        elif (
            event.get("resource") == "/carriers/{carrierId}"
            and event.get("httpMethod") == "PATCH"
        ):
            carrier_id = (
                event["pathParameters"]["carrierId"]
            )

            body = json.loads(event["body"])

            row = execute_returning(
                UPDATE_CARRIER_SQL,
                (
                    body["name"],
                    body["email"],
                    body["phone"],
                    body["is_active"],
                    carrier_id
                )
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Carrier not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_carrier(row)
                )
            }

        elif (
            event.get("resource") == "/carriers/{carrierId}"
            and event.get("httpMethod") == "DELETE"
        ):
            carrier_id = (
                event["pathParameters"]["carrierId"]
            )

            row = execute_returning(
                DELETE_CARRIER_SQL,
                (carrier_id,)
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Carrier not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_carrier(row)
                )
            }

        elif (
            event.get("resource") == "/shipments/{shipmentId}"
            and event.get("httpMethod") == "PATCH"
        ):
            shipment_id = (
                event["pathParameters"]["shipmentId"]
            )

            body = json.loads(event["body"])

            row = execute_returning(
                UPDATE_SHIPMENT_SQL,
                (
                    body["order_id"],
                    body["origin"],
                    body["destination"],
                    body["weight_kg"],
                    shipment_id
                )
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Shipment not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_shipment(row)
                )
            }

        elif (
            event.get("resource") == "/shipments/{shipmentId}"
            and event.get("httpMethod") == "DELETE"
        ):
            shipment_id = (
                event["pathParameters"]["shipmentId"]
            )

            row = execute_returning(
                DELETE_SHIPMENT_SQL,
                (shipment_id,)
            )

            if row is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps(
                        {"message": "Shipment not found"}
                    )
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    row_to_shipment(row)
                )
            }

        elif (
            event.get("resource") == "/statusupdates"
            and event.get("httpMethod") == "POST"
        ):
            body = json.loads(event["body"])

            if body["status"] not in VALID_STATUSES:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid status"
                    })
                }

            shipment = fetch_one(
                """
                SELECT shipment_id
                FROM shipments
                WHERE shipment_id = %s
                """,
                (body["shipment_id"],)
            )

            if shipment is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Shipment not found"
                    })
                }

            carrier = fetch_one(
                """
                SELECT carrier_id
                FROM carriers
                WHERE carrier_id = %s
                """,
                (body["carrier_id"],)
            )

            if carrier is None:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Carrier not found"
                    })
                }

            row = execute_returning(
                CREATE_STATUS_UPDATE_SQL,
                (
                    body["shipment_id"],
                    body["carrier_id"],
                    body["status"],
                    body["location"],
                    body["notes"]
                )
            )

            return {
                "statusCode": 201,
                "body": json.dumps(
                    row_to_status_update(row)
                )
            }

        elif (
            event.get("resource") == "/statusupdates/{shipmentId}"
            and event.get("httpMethod") == "GET"
        ):
            shipment_id = (
                event["pathParameters"]["shipmentId"]
            )

            rows = fetch_all(
                GET_STATUS_UPDATES_SQL,
                (shipment_id,)
            )

            result = [
                row_to_status_update(row)
                for row in rows
            ]

            return {
                "statusCode": 200,
                "body": json.dumps(result)
            }


        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "Not found"
            })
        }

    
HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
