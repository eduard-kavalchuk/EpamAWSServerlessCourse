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
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        yield conn, cur

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()


def fetch_one(query, params=None):
    with get_cursor() as (_, cur):
        if params is None:
            cur.execute(query)
        else:
            cur.execute(query, params)
        return cur.fetchone()


def fetch_all(query, params=None):
    with get_cursor() as (_, cur):
        if params is None:
            cur.execute(query)
        else:
            cur.execute(query, params)

        return cur.fetchall()


def execute(query, params=None):
    with get_cursor() as (conn, cur):
        try:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)

            conn.commit()

        except Exception:
            conn.rollback()
            raise


def execute_returning(query, params=None):
    with get_cursor() as (conn, cur):
        try:
            if params is None:
                cur.execute(query)
            else:
                cur.execute(query, params)

            result = cur.fetchone()
            conn.commit()

            return result
        
        except Exception:
            conn.rollback()
            raise


def execute_many(query, values):
    with get_cursor() as (conn, cur):
        try:
            cur.executemany(query, values)
            conn.commit()

        except Exception:
            conn.rollback()
            raise


