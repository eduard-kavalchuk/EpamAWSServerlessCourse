from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

import csv

from io import StringIO
from commons.db import execute_many

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
        except:
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


def process_carriers(content):
    rows = parse_csv(content)

    print(
        f"Processing carriers.csv "
        f"({len(rows)} rows)"
    )

    values = []

    for row in rows:
        values.append(
            (
                row["carrier_id"],
                row["name"],
                row["email"],
                row["phone"],
                row["is_active"].lower() == "true"
            )
        )

    for chunk in chunks(values, BATCH_SIZE):
        execute_many(
            CARRIERS_INSERT_SQL,
            chunk
        )


def process_status_updates(content):
    rows = parse_csv(content)

    print(
        f"Processing status_updates.csv "
        f"({len(rows)} rows)"
    )

    values = []

    for row in rows:
        status = row["status"]

        if status not in VALID_STATUSES:
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

class BatchProcessor(AbstractLambda):

    def validate_request(self, event):
        print("validate_request invoked")
        return None

    def handle_request(self, event, context):
        print("handle_request invoked")

        record = event["Records"][0]

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

        if key.endswith("shipments.csv"):

            process_shipments(content)

        elif key.endswith("carriers.csv"):

            process_carriers(content)

        elif key.endswith("status_updates.csv"):

            process_status_updates(content)

        else:
            print(
                f"Unsupported file: {key}"
            )

        return {
            "statusCode": 200,
            "body": "Processed"
        }
    

HANDLER = BatchProcessor()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
