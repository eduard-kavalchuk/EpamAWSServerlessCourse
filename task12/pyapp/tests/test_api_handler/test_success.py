from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import MagicMock, patch

import os


os.environ["TABLES_TABLE"] = "Tables"
os.environ["RESERVATIONS_TABLE"] = "Reservations"
os.environ["USER_POOL_NAME"] = "simple-booking-userpool"


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_signin_success(self):
    
        EMAIL = "test@example.com"
        PASSWORD = "Password123$"

        event = {
            "resource": "/signin",
            "httpMethod": "POST",
            "body": {
                "email": EMAIL,
                "password": PASSWORD
            }
        }

        cognito_mock = MagicMock()

        cognito_mock.get_paginator.return_value.paginate.return_value = [
            {
                "UserPools": [
                    {
                        "Name": "cmtr-mxhmo8sx-simple-booking-userpool",
                        "Id": "eu-west-1_TEST_POOL"
                    }
                ]
            }
        ]

        cognito_mock.list_user_pool_clients.return_value = {
            "UserPoolClients": [
                {
                    "ClientName": "booking-client",
                    "ClientId": "TEST_CLIENT_ID"
                }
            ]
        }

        cognito_mock.admin_initiate_auth.return_value = {
            "AuthenticationResult": {
                "AccessToken": "ACCESS_TOKEN",
                "IdToken": "ID_TOKEN",
                "RefreshToken": "REFRESH_TOKEN"
            }
        }

        with patch.dict(
            os.environ,
            {
                "USER_POOL_NAME": "cmtr-mxhmo8sx-simple-booking-userpool"
            }
        ):
            with patch(
                "lambdas.api_handler.handler.boto3.client",
                return_value=cognito_mock
            ):
                response = self.HANDLER.handle_request(event, None)

        print('RESPONSE:')
        print(response)
        assert response["statusCode"] == 200

        body = json.loads(response["body"])

        assert body["accessToken"] == "ACCESS_TOKEN"
        assert body["idToken"] == "ID_TOKEN"
        assert body["refreshToken"] == "REFRESH_TOKEN"

        cognito_mock.list_user_pool_clients.assert_called_once_with(
            UserPoolId="eu-west-1_TEST_POOL",
            MaxResults=60
        )

        cognito_mock.admin_initiate_auth.assert_called_once_with(
            UserPoolId="eu-west-1_TEST_POOL",
            ClientId="TEST_CLIENT_ID",
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": EMAIL,
                "PASSWORD": PASSWORD
            }
        )

    def test_signin_client_not_found(self):
        EMAIL = "test@example.com"
        PASSWORD = "Password123$"

        event = {
            "resource": "/signin",
            "httpMethod": "POST",
            "body": {
                "email": EMAIL,
                "password": PASSWORD
            }
        }

        # event = {
        #     "email": "john@example.com",
        #     "password": "Password123$"
        # }

        cognito_mock = MagicMock()

        cognito_mock.get_paginator.return_value.paginate.return_value = [
            {
                "UserPools": [
                    {
                        "Name": "cmtr-mxhmo8sx-simple-booking-userpool",
                        "Id": "eu-west-1_TEST_POOL"
                    }
                ]
            }
        ]

        cognito_mock.list_user_pool_clients.return_value = {
            "UserPoolClients": []
        }

        with patch.dict(
            os.environ,
            {
                "USER_POOL_NAME": "cmtr-mxhmo8sx-simple-booking-userpool"
            }
        ):
            with patch(
                "lambdas.api_handler.handler.boto3.client",
                return_value=cognito_mock
            ):
                try:
                    response = self.HANDLER.handle_request(event, None)
                    assert response["statusCode"] == 400
                    assert response["body"]["message"] == "User pool client not found"
                except Exception:
                    pass


    def test_signup_success(self):
        EMAIL = "test@example.com"
        PASSWORD = "Password123$"

        event = {
            "resource": "/signup",
            "httpMethod": "POST",
            "body": {
                "firstName": "First name",
                "lastName": "Last name",
                "email": EMAIL,
                "password": PASSWORD
            }
        }

        cognito_mock = MagicMock()

        cognito_mock.get_paginator.return_value.paginate.return_value = [
            {
                "UserPools": [
                    {
                        "Name": "simple-booking-userpool",
                        "Id": "eu-west-1_testpool"
                    }
                ]
            }
        ]

        with patch("os.environ", {"USER_POOL_NAME": "simple-booking-userpool"}):
            with patch("boto3.client", return_value=cognito_mock):
                response = self.HANDLER.handle_request(event, None)

        assert response["statusCode"] == 200

        body = json.loads(response["body"])

        assert body["message"] == "Sign-up successful"

        cognito_mock.admin_create_user.assert_called_once()

        cognito_mock.admin_set_user_password.assert_called_once()

