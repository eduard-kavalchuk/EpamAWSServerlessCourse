import json
import os

from contextlib import contextmanager

import boto3
import pg8000

_cached_secret = None


def get_secret():
    global _cached_secret

    if _cached_secret:
        return _cached_secret

    secret_name = os.environ["DB_SECRET_NAME"]

    client = boto3.client("secretsmanager")

    response = client.get_secret_value(
        SecretId=secret_name
    )

    _cached_secret = json.loads(
        response["SecretString"]
    )

    return _cached_secret


def get_connection():
    secret = get_secret()

    return pg8000.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=secret["username"],
        password=secret["password"],
        port=5432,
        timeout=10
    )


@contextmanager
def get_cursor():
    conn = get_connection()

    try:
        cur = conn.cursor()
        yield conn, cur
    finally:
        cur.close()
        conn.close()


def execute(query):
    with get_cursor() as (conn, cur):
        cur.execute(query)
        conn.commit()