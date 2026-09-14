from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

from unittest.mock import MagicMock, patch
import pytest
import os
import datetime
import json


os.environ["DB_HOST"] = "endpoint"
os.environ["DB_SECRET_NAME"] = "logistic-cluster"
os.environ["DB_NAME"] = "logisticdb"


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


class TestSuccess(ApiHandlerLambdaTestCase):
    class TestSuccess:

        def test_initdb(self):
            with patch(
                "lambdas.api_handler.handler.execute"
            ) as mock_execute:

                event = {
                    "resource": "/initdb",
                    "httpMethod": "POST"
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200

                mock_execute.assert_called_once()


        def test_lambda_returns_200(self):
            with patch(
                "lambdas.api_handler.handler.get_connection"
            ) as mock_get_connection:
                mock_conn = MagicMock()
                mock_cursor = MagicMock()

                mock_get_connection.return_value = mock_conn

                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchone.return_value = (1,)

                response = self.HANDLER.handle_request(dict(), None)

                assert response["statusCode"] == 200
                assert response["body"] == "(1,)"

                mock_cursor.execute.assert_called_once_with("SELECT 1")
                mock_cursor.close.assert_called_once()
                mock_conn.close.assert_called_once()


        def test_connection_closed_on_sql_error(self):
            with patch(
                "lambdas.api_handler.handler.get_connection"
            ) as mock_get_connection:

                mock_conn = MagicMock()
                mock_cursor = MagicMock()

                mock_get_connection.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor

                mock_cursor.execute.side_effect = Exception("DB error")

                with pytest.raises(Exception):
                    self.HANDLER.handle_request(dict(), None)

                mock_cursor.close.assert_called_once()
                mock_conn.close.assert_called_once()


        def test_create_shipment(self):
            with patch(
                "lambdas.api_handler.handler.get_connection"
            ) as mock_execute:

                mock_execute.return_value = (
                    "s1",
                    "o1",
                    "Minsk",
                    "Warsaw",
                    10.5,
                    datetime.now()
                )

                event = {
                    "resource": "/shipments",
                    "httpMethod": "POST",
                    "body": json.dumps({
                        "shipment_id": "s1",
                        "order_id": "o1",
                        "origin": "Minsk",
                        "destination": "Warsaw",
                        "weight_kg": 10.5
                    })
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 201


        def test_get_shipment(self):
            with patch(
                "lambdas.api_handler.handler.fetch_one"
            ) as mock_fetch:

                mock_fetch.return_value = (
                    "s1",
                    "o1",
                    "Minsk",
                    "Warsaw",
                    10.5,
                    datetime.now()
                )

                event = {
                    "resource": "/shipments/{shipmentId}",
                    "httpMethod": "GET",
                    "pathParameters": {
                        "shipmentId": "s1"
                    }
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200


        def test_create_carrier(self):
            with patch(
                "lambdas.api_handler.handler.get_connection"
            ) as mock_execute:

                mock_execute.return_value = (
                    "s1",
                    "my_carrier",
                    "carrier@shipment.com",
                    "1234567890",
                    True,
                )

                event = {
                    "resource": "/shipments",
                    "httpMethod": "POST",
                    "body": json.dumps({
                        "carrier_id": "s1",
                        "name": "my_carrier",
                        "email": "carrier@shipment.com",
                        "phone": "1234567890",
                        "is_active": True
                    })
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 201


        def test_get_carrier(self):
            with patch(
                "lambdas.api_handler.handler.fetch_one"
            ) as mock_fetch:

                mock_fetch.return_value = (
                    "s1",
                    "my_carrier",
                    "carrier@shipment.com",
                    "1234567890",
                    True,
                )

                event = {
                    "resource": "/carriers/{carrierId}",
                    "httpMethod": "GET",
                    "pathParameters": {
                        "carrierId": "s1"
                    }
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200


        def test_patch_carrier(self):
            with patch(
                "lambdas.api_handler.handler.fetch_one"
            ) as mock_execute:

                mock_execute.return_value = (
                    "c1",
                    "DHL",
                    "dhl@test.com",
                    "+12345",
                    True
                )

                event = {
                    "resource": "/carriers/{carrierId}",
                    "httpMethod": "PATCH",
                    "pathParameters": {
                        "carrierId": "c1"
                    },
                    "body": json.dumps({
                        "name": "DHL",
                        "email": "dhl@test.com",
                        "phone": "+12345",
                        "is_active": True
                    })
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200

                mock_execute.assert_called_once()


        def test_delete_carrier(self):
            with patch(
                "lambdas.api_handler.handler.execute_returning"
            ) as mock_execute:

                mock_execute.return_value = (
                    "c1",
                    "DHL",
                    "dhl@test.com",
                    "+12345",
                    True
                )

                event = {
                    "resource": "/carriers/{carrierId}",
                    "httpMethod": "DELETE",
                    "pathParameters": {
                        "carrierId": "c1"
                    }
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200

                mock_execute.assert_called_once_with(
                    DELETE_CARRIER_SQL,
                    ("c1",)
                )

        def test_patch_shipment(self):
            with patch(
                "lambdas.api_handler.handler.execute_returning"
            ) as mock_execute:

                mock_execute.return_value = (
                    "s1",
                    "o1",
                    "Minsk",
                    "Warsaw",
                    10.5,
                    datetime.now()
                )

                event = {
                    "resource": "/shipments/{shipmentId}",
                    "httpMethod": "PATCH",
                    "pathParameters": {
                        "shipmentId": "s1"
                    },
                    "body": json.dumps({
                        "order_id": "o1",
                        "origin": "Minsk",
                        "destination": "Warsaw",
                        "weight_kg": 10.5
                    })
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200


        def test_delete_shipment(self):
            with patch(
                "lambdas.api_handler.handler.execute_returning"
            ) as mock_execute:

                mock_execute.return_value = (
                    "s1",
                    "o1",
                    "Minsk",
                    "Warsaw",
                    10.5,
                    datetime.now()
                )

                event = {
                    "resource": "/shipments/{shipmentId}",
                    "httpMethod": "DELETE",
                    "pathParameters": {
                        "shipmentId": "s1"
                    }
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200


        def test_create_status_update(self):
            with patch(
                "lambdas.api_handler.handler.execute_returning"
            ) as mock_execute:

                mock_execute.return_value = (
                    1,
                    "s1",
                    "c1",
                    "CREATED",
                    "Minsk",
                    "Created",
                    datetime.now()
                )

                event = {
                    "resource": "/statusupdates",
                    "httpMethod": "POST",
                    "body": json.dumps({
                        "shipment_id": "s1",
                        "carrier_id": "c1",
                        "status": "CREATED",
                        "location": "Minsk",
                        "notes": "Created"
                    })
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 201


        def test_get_status_updates(self):
            with patch(
                "lambdas.api_handler.handler.fetch_all"
            ) as mock_fetch:

                mock_fetch.return_value = [
                    (
                        1,
                        "s1",
                        "c1",
                        "CREATED",
                        "Minsk",
                        "Created",
                        datetime.now()
                    )
                ]

                event = {
                    "resource": "/statusupdates/{shipmentId}",
                    "httpMethod": "GET",
                    "pathParameters": {
                        "shipmentId": "s1"
                    }
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200


