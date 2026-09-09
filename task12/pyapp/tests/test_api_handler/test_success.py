from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import MagicMock, patch

import os
import uuid

os.environ["TABLES_TABLE"] = "Tables"
os.environ["RESERVATIONS_TABLE"] = "Reservations"
os.environ["USER_POOL_NAME"] = "simple-booking-userpool"


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_create_overlapping_reservation(self):
        event = {
            "resource": "/reservations",
            "httpMethod": "POST",
            "body": {
                "tableNumber": 1,
                "clientName": "John Smith",
                "phoneNumber": "+375291112233",
                "date": "2026-09-09",
                "slotTimeStart": "13:00",
                "slotTimeEnd": "15:00"
            }
        }

        tables_table_mock = MagicMock()
        reservations_table_mock = MagicMock()

        tables_table_mock.scan.return_value = {
            "Items": [
                {
                    "id": 1,
                    "number": 1,
                    "places": 4,
                    "isVip": False
                }
            ]
        }

        reservations_table_mock.scan.side_effect = [
            {
                "Items": []
            },
            {
                "Items": [
                    {
                        "id": "1111",
                        "tableNumber": 1,
                        "clientName": "John Smith",
                        "phoneNumber": "+375291112233",
                        "date": "2026-09-09",
                        "slotTimeStart": "13:00",
                        "slotTimeEnd": "15:00"
                    }
                ]
            }
        ]

        with patch(
            "lambdas.api_handler.handler.get_tables_table",
            return_value=tables_table_mock
        ), patch(
            "lambdas.api_handler.handler.get_reservations_table",
            return_value=reservations_table_mock
        ):

            response1 = self.HANDLER._create_reservation(event)
            response2 = self.HANDLER._create_reservation(event)

        assert response1["statusCode"] == 200
        assert response2["statusCode"] == 400


    def test_create_reservation_success(self):
        event = {
            "resource": "/reservations",
            "httpMethod": "POST",
            "body": {
                "tableNumber": 1,
                "clientName": "John Smith",
                "phoneNumber": "+375291112233",
                "date": "2026-09-09",
                "slotTimeStart": "13:00",
                "slotTimeEnd": "15:00"
            }
        }

        tables_table_mock = MagicMock()
        reservations_table_mock = MagicMock()

        tables_table_mock.scan.return_value = {
            "Items": [
                {
                    "id": 1,
                    "number": 1,
                    "places": 4,
                    "isVip": False
                }
            ]
        }

        with patch(
            "lambdas.api_handler.handler.get_tables_table",
            return_value=tables_table_mock
        ), patch(
            "lambdas.api_handler.handler.get_reservations_table",
            return_value=reservations_table_mock
        ), patch(
            "lambdas.api_handler.handler.uuid.uuid4",
            return_value="11111111-2222-3333-4444-555555555555"
        ):
            response = self.HANDLER._create_reservation(event)

        assert response["statusCode"] == 200

        body = json.loads(response["body"])

        assert body["reservationId"] == \
            "11111111-2222-3333-4444-555555555555"

        reservations_table_mock.put_item.assert_called_once()


    def test_get_reservations(self):
        with patch(
            "lambdas.api_handler.handler.boto3.resource"
        ) as mock_resource:

            mock_table = MagicMock()

            mock_table.scan.return_value = {
                "Items": [
                    {
                        "id": str(uuid.uuid4()),
                        "tableNumber": 1,
                        "clientName": "Client name",
                        "phoneNumber": "123-45-67",
                        "date": "2026-09-10",
                        "slotTimeStart": "09:30",
                        "slotTimeEnd": "17:45",
                    }
                ]
            }

            mock_resource.return_value.Table.return_value = mock_table

            response = self.HANDLER._get_reservations()
            body = json.loads(response["body"])

            self.assertEqual(response["statusCode"], 200)
            self.assertEqual(len(body["reservations"]), 1)
            self.assertEqual(body["reservations"][0]["tableNumber"], 1)


    def test_get_tables(self):
        with patch(
            "lambdas.api_handler.handler.boto3.resource"
        ) as mock_resource:

            mock_table = MagicMock()

            mock_table.scan.return_value = {
                "Items": [
                    {
                        "id": 1,
                        "number": 1,
                        "places": 4,
                        "isVip": False
                    }
                ]
            }

            mock_resource.return_value.Table.return_value = mock_table

            response = self.HANDLER._get_tables()
            body = json.loads(response["body"])

            self.assertEqual(response["statusCode"], 200)
            self.assertEqual(len(body["tables"]), 1)
            self.assertEqual(body["tables"][0]["id"], 1)
            self.assertEqual(body["tables"][0]["number"], 1)


    def test_create_table(self):
        with patch(
            "lambdas.api_handler.handler.boto3.resource"
        ) as mock_resource:
            
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table

            event = {
                "resource": "/tables",
                "httpMethod": "POST",
                "body": {
                    "id": 123,
                    "number": 1,
                    "places": 5,
                    "isVip": False,
                    "minOrder": 100
                }
            }

            response = self.HANDLER._create_table(event)
            body = json.loads(response["body"])

            self.assertEqual(response["statusCode"], 200)
            self.assertEqual(body["id"], 123)

            mock_table.put_item.assert_called_once()

            # Verify exactly what is written to DynamoDB
            saved_item = mock_table.put_item.call_args.kwargs["Item"]

            self.assertEqual(saved_item["id"], 123)
            self.assertEqual(saved_item["number"], 1)
            self.assertEqual(saved_item["places"], 5)
            self.assertEqual(saved_item["isVip"], False)
            self.assertEqual(saved_item["minOrder"], 100)


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

