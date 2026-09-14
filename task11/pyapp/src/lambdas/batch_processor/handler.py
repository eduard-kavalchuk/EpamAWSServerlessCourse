from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import csv

from io import StringIO
from commons.db import execute_many, fetch_all

import boto3

_LOG = get_logger(__name__)

SHIPMENTS_INSERT_SQL = """
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
    %s
)
ON CONFLICT (shipment_id) DO NOTHING
"""

CARRIERS_INSERT_SQL = """
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
ON CONFLICT (carrier_id) DO NOTHING
"""

STATUS_UPDATES_INSERT_SQL = """
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
    %s
)
"""

VALID_STATUSES = {
    "CREATED",
    "IN_TRANSIT",
    "DELAYED",
    "DELIVERED",
    "CANCELLED"
}

BATCH_SIZE = 1000

def download_s3_object(bucket, key):
    s3 = boto3.client("s3")

    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    return response["Body"].read().decode("utf-8")
    
    
def parse_csv(content):
    return list(
        csv.DictReader(
            StringIO(content)
        )
    )
    
    
def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def process_shipments(content):
    rows = parse_csv(content)

    print(
        f"Processing shipments.csv "
        f"({len(rows)} rows)"
    )

    values = []

    for row in rows:
        try:
            weight = float(row["weight_kg"])
        except (ValueError, TypeError):
            continue

        if not row["shipment_id"]:
            continue

        if not row["order_id"]:
            continue

        values.append(
            (
                row["shipment_id"],
                row["order_id"],
                row["origin"],
                row["destination"],
                weight,
                row["created_at"]
            )
        )

    for chunk in chunks(values, BATCH_SIZE):
        execute_many(
            SHIPMENTS_INSERT_SQL,
            chunk
        )

    print(
        f"Inserted {len(values)} shipment rows"
    )


def process_carriers(content):
    rows = parse_csv(content)

    print(
        f"Processing carriers.csv "
        f"({len(rows)} rows)"
    )

    values = []

    for row in rows:
        if not row["carrier_id"]:
            continue

        values.append(
            (
                row["carrier_id"],
                row["name"],
                row["email"],
                row["phone"],
                str(row["is_active"]).strip().lower() in (
                    "true",
                    "1",
                    "yes"
                )
            )
        )

    for chunk in chunks(values, BATCH_SIZE):
        execute_many(
            CARRIERS_INSERT_SQL,
            chunk
        )

    print(
        f"Inserted {len(values)} carrier rows"
    )


def process_status_updates(content):
    rows = parse_csv(content)

    print(
        f"Processing status_updates.csv "
        f"({len(rows)} rows)"
    )

    existing_shipments = {
        row[0]
        for row in fetch_all(
            "SELECT shipment_id FROM shipments"
        )
    }

    existing_carriers = {
        row[0]
        for row in fetch_all(
            "SELECT carrier_id FROM carriers"
        )
    }

    values = []

    for row in rows:
        if row["shipment_id"] not in existing_shipments:
            continue

        if row["carrier_id"] not in existing_carriers:
            continue

        status = row["status"]

        if status not in VALID_STATUSES:
            continue

        if not row["shipment_id"]:
            continue

        if not row["carrier_id"]:
            continue

        values.append(
            (
                row["shipment_id"],
                row["carrier_id"],
                row["status"],
                row["location"],
                row["notes"],
                row["timestamp"]
            )
        )

    for chunk in chunks(values, BATCH_SIZE):
        execute_many(
            STATUS_UPDATES_INSERT_SQL,
            chunk
        )

    print(
        f"Inserted {len(values)} status updates rows"
    )


class BatchProcessor(AbstractLambda):

    def validate_request(self, event):
        print("validate_request invoked")
        return None

    def handle_request(self, event, context):
        print("handle_request invoked")

        # record = event["Records"][0]

        for record in event["Records"]:

            bucket = (
                record["s3"]["bucket"]["name"]
            )

            key = (
                record["s3"]["object"]["key"]
            )

            print(
                f"bucket={bucket}, "
                f"key={key}"
            )

            content = download_s3_object(
                bucket,
                key
            )

            filename = key.lower()

            if filename.endswith("shipments.csv"):

                process_shipments(content)

            elif filename.endswith("carriers.csv"):

                process_carriers(content)

            elif filename.endswith("status_updates.csv"):

                process_status_updates(content)

            else:
                print(
                    f"Unsupported file: {filename}"
                )

        return {
            "statusCode": 200,
            "body": "Processed"
        }
    

HANDLER = BatchProcessor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
