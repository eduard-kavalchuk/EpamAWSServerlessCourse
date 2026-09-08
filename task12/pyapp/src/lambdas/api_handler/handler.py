import json
import uuid
import boto3
import os
import re

from datetime import datetime, timezone

from commons.log_helper import get_logger
from commons.abstract_lambda import AbstractLambda

_LOG = get_logger(__name__)

def get_tables_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["TABLES_TABLE"])

def get_reservations_table():
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(os.environ["RESERVATIONS_TABLE"])


def get_pool_name():
    return os.environ["USER_POOL_NAME"]


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

PASSWORD_PATTERN = re.compile(
    r"^[A-Za-z0-9$%^*\-_]{12,}$"
)


class ApiHandler(AbstractLambda):

    def validate_request(self, event) -> dict:
        pass
        
    def handle_request(self, event, context):
        print("USER_POOL_NAME =", os.environ["USER_POOL_NAME"])

        return self._signup(event)
    
        # print(json.dumps(event))
        # print("CONTEXT:", context)
        # print("CONTEXT TYPE:", type(context))

        # path = event.get("resource")
        # method = event.get("httpMethod")

        # if path == "/signup" and method == "POST":
        #     print("SIGNUP HANDLER CALLED")
        #     return self._signup(event)
        
        # return {
        #     "statusCode": 200,
        #     "body": json.dumps({
        #         "resource": event.get("resource"),
        #         "path": event.get("path"),
        #         "httpMethod": event.get("httpMethod")
        #     })
        # }

    def _signup(self, event):
        try:
            # body = json.loads(event.get("body") or "{}")
            print(f"SIGNUP REQUEST: {event}")

            first_name = event["firstName"]
            last_name = event["lastName"]
            email = event["email"]
            password = event["password"]

            if not EMAIL_PATTERN.match(email):
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
                    "exception": ex
                })
            }

        except Exception as exc:
            print(f"Signup error: {exc}")

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": str(exc)
                })
            }
    

HANDLER = ApiHandler()


def lambda_handler(event, context):
    return HANDLER.lambda_handler(event=event, context=context)
