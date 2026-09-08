from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import MagicMock, patch

import os

os.environ["TABLES_TABLE"] = "Tables"
os.environ["RESERVATIONS_TABLE"] = "Reservations"
os.environ["USER_POOL_NAME"] = "simple-booking-userpool"


class TestSuccess(ApiHandlerLambdaTestCase):

    # def test_generic(self):
    #     event = {
    #         "resource": "This is a resource",
    #         "path": "This is path",
    #         "httpMethod": "This is httpMethod"
    #     }

    #     response = self.HANDLER.handle_request(event, None)

    #     self.assertEqual(response["statusCode"], 200)


    def test_signup_success(self):
        event = {
            "resource": "/signup",
            "httpMethod": "POST",
            "firstName": "First name",
            "lastName": "Last name",
            "email": "test@example.com",
            "password": "Password123$"
            # "body": json.dumps({
            #     "firstName": "First name",
            #     "lastName": "Last name",
            #     "email": "test@example.com",
            #     "password": "Password123$"
            # })
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

        print("RESPONCE:")
        print(response)
        assert response["statusCode"] == 200

        body = json.loads(response["body"])

        assert body["message"] == "Sign-up successful"

        cognito_mock.admin_create_user.assert_called_once()

        cognito_mock.admin_set_user_password.assert_called_once()

