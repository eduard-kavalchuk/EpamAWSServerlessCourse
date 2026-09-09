import json
import uuid
import boto3
import os
import re

from datetime import datetime, date

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

from decimal import Decimal

_LOG = get_logger(__name__)

def get_tables_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["TABLES_TABLE"])

def get_reservations_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["RESERVATIONS_TABLE"])

def get_pool_name():
    return os.environ["USER_POOL_NAME"]

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError


def is_valid_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(value):
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
)

PASSWORD_PATTERN = re.compile(
    r"^[A-Za-z0-9$%^*\-_]{12,}$"
)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass

        
    def handle_request(self, event, context):
        if not isinstance(event, dict):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Invalid request"
                })
            }

        resource = event["resource"]
        method = event["httpMethod"]

        if resource == "/signup" and method == "POST":
            return self._signup(event)

        if resource == "/signin" and method == "POST":
            return self._signin(event)

        if resource == "/tables" and method == "GET":
            return self._get_tables()

        if resource == "/tables" and method == "POST":
            return self._create_table(event)

        if resource == "/reservations" and method == "GET":
            return self._get_reservations()

        if resource == "/reservations" and method == "POST":
            return self._create_reservation(event)

        if resource == "/tables/{tableId}" and method == "GET":
            return self._get_table(event)

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid request"
            })
        }

    def _get_table(self, event):
        try:
            table_id = int(event["tableId"])

            tables = get_tables_table()

            response = tables.get_item(
                Key={
                    "id": table_id
                }
            )

            item = response.get("Item")

            if not item:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Table not found"
                    })
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    item,
                    default=decimal_default
                )
            }

        except Exception as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(ex)
                })
            }

    def _get_reservations(self):
        try:
            response = get_reservations_table().scan()
            items = response["Items"]

            reservations = []

            for item in items:
                reservations.append({
                    "tableNumber": item["tableNumber"],
                    "clientName": item["clientName"],
                    "phoneNumber": item["phoneNumber"],
                    "date": item["date"],
                    "slotTimeStart": item["slotTimeStart"],
                    "slotTimeEnd": item["slotTimeEnd"]
                })

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "reservations": reservations
                    },
                    default=decimal_default
                )
            }

        except Exception as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(ex)
                })
            }

    def _create_reservation(self, event):
        try:
            body = event["body"]

            if not is_valid_date(body["date"]):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid date"
                    })
                }

            new_reservation_date = datetime.strptime(body["date"], "%Y-%m-%d").date()

            if new_reservation_date < date.today():
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid date"
                    })
                }

            if not is_valid_time(body["slotTimeStart"]):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid slotTimeStart"
                    })
                }

            if not is_valid_time(body["slotTimeEnd"]):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid slotTimeEnd"
                    })
                }

            start_time = datetime.strptime(body["slotTimeStart"], "%H:%M").time()
            end_time = datetime.strptime(body["slotTimeEnd"], "%H:%M").time()
            if start_time > end_time:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid slotTimeEnd"
                    })
                }

            tables = json.loads(self._get_tables()['body'])['tables']
            table_ids = [table["id"] for table in tables]

            if body["tableNumber"] not in table_ids:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid tableNumber"
                    })
                }

            reservations = json.loads(self._get_reservations()['body'])["reservations"]

            for reservation in reservations:
                reservation_slot_start = datetime.strptime(reservation["slotTimeStart"], "%H:%M").time()
                reservation_slot_end = datetime.strptime(reservation["slotTimeEnd"], "%H:%M").time()
                reservation_date = datetime.strptime(body["date"], "%Y-%m-%d").date()
                if new_reservation_date == reservation_date:
                    if max(reservation_slot_start, start_time) < max(reservation_slot_end, end_time):
                        return {
                            "statusCode": 400,
                            "body": json.dumps({
                                "message": "Conflicting reservations"
                            })
                        }

            reservationId = str(uuid.uuid4())

            item = {
                "id": reservationId,
                "tableNumber": body["tableNumber"],
                "clientName": body["clientName"],
                "phoneNumber": body["phoneNumber"],
                "date": body["date"],
                "slotTimeStart": body["slotTimeStart"],
                "slotTimeEnd": body["slotTimeEnd"],
            }

            table = get_reservations_table()
            table.put_item(Item=item)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "reservationId": reservationId
                })
            }

        except Exception as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(ex)
                })
            }

    def _get_tables(self):
        try:
            response = get_tables_table().scan()

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "tables": response.get("Items", [])
                    },
                    default=decimal_default
                )
            }

        except Exception as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(ex)
                })
            }

    def _create_table(self, event):
        try:
            body = event["body"]

            item = {
                "id": body["id"],
                "number": body["number"],
                "places": body["places"],
                "isVip": body["isVip"]
            }

            if "minOrder" in body:
                item["minOrder"] = body["minOrder"]

            table = get_tables_table()

            table.put_item(Item=item)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "id": body["id"]
                })
            }

        except Exception as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(ex)
                })
            }


    def _signin(self, event):
        try:
            body = event["body"]

            email = body["email"]
            password = body["password"]

            user_pool_name = os.environ["USER_POOL_NAME"]
            cognito = boto3.client("cognito-idp")
            user_pool_id = None
            paginator = cognito.get_paginator("list_user_pools")

            for page in paginator.paginate(MaxResults=60):
                for pool in page["UserPools"]:
                    if pool["Name"] == user_pool_name:
                        user_pool_id = pool["Id"]
                        break

                if user_pool_id:
                    break

            if not user_pool_id:
                raise Exception("User pool not found")

            response = cognito.list_user_pool_clients(
                UserPoolId=user_pool_id,
                MaxResults=60
            )

            client_id = None
            for client in response["UserPoolClients"]:
                if client["ClientName"] == "booking-client":
                    client_id = client["ClientId"]

            if not client_id:
                raise Exception("User pool client not found")

            response = cognito.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password
                }
            )

            tokens = response["AuthenticationResult"]

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "idToken": tokens["IdToken"],
                })
            }
        except KeyError as exc:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required field",
                    "exception": str(exc)
                })
            }

        except Exception as exc:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(exc)
                })
            }

    
    def _signup(self, event):
        try:
            body = event["body"]

            first_name = body["firstName"]
            last_name = body["lastName"]
            email = body["email"]
            password = body["password"]

            if not isinstance(email, str):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid email"
                    })
                }

            email = email.strip()

            if len(email) == 0:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid email"
                    })
                }

            if not EMAIL_PATTERN.fullmatch(email):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid email"
                    })
                }

            local_part, domain_part = email.rsplit("@", 1)
            if (
                local_part.startswith(".")
                or local_part.endswith(".")
                or ".." in local_part
                or domain_part.startswith(".")
                or domain_part.endswith(".")
                or ".." in domain_part
            ):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid email"
                    })
                }

            if not PASSWORD_PATTERN.match(password):
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid password"
                    })
                }

            user_pool_name = os.environ["USER_POOL_NAME"]

            cognito = boto3.client("cognito-idp")

            user_pool_id = None

            paginator = cognito.get_paginator("list_user_pools")

            for page in paginator.paginate(MaxResults=60):
                for pool in page["UserPools"]:
                    if pool["Name"] == user_pool_name:
                        user_pool_id = pool["Id"]
                        break

                if user_pool_id:
                    break

            if not user_pool_id:
                raise Exception("User pool not found")

            try:
                cognito.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=email,
                    UserAttributes=[
                        {
                            "Name": "email",
                            "Value": email
                        },
                        {
                            "Name": "given_name",
                            "Value": first_name
                        },
                        {
                            "Name": "family_name",
                            "Value": last_name
                        },
                        {
                            "Name": "email_verified",
                            "Value": "true"
                        }
                    ],
                    MessageAction="SUPPRESS"
                )

                cognito.admin_set_user_password(
                    UserPoolId=user_pool_id,
                    Username=email,
                    Password=password,
                    Permanent=True
                )
            except cognito.exceptions.NotAuthorizedException:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Invalid email or password"
                    })
                }

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Sign-up successful"
                })
            }

        except KeyError as ex:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required field",
                    "exception": str(ex)
                })
            }

        except Exception as exc:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(exc)
                })
            }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
