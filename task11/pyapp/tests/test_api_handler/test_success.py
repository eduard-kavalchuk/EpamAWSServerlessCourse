from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

from unittest.mock import MagicMock, patch
import pytest
import os


os.environ["DB_HOST"] = "endpoint"
os.environ["DB_SECRET_NAME"] = "logistic-cluster"
os.environ["DB_NAME"] = "logisticdb"


class TestSuccess(ApiHandlerLambdaTestCase):
    class TestSuccess:

    # def test_lambda_returns_200(self):
    #     with patch(
    #         "lambdas.api_handler.handler.execute"
    #     ) as mock_fetch_one:
            
    #         mock_fetch_one.return_value = (1,)

    #         result = self.HANDLER.handle_request(dict(), None)

    #         assert result["statusCode"] == 200
    #         assert result["body"] == "(1,)"

    #     mock_fetch_one.assert_called_once_with("SELECT 1")
    

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


    # def test_lambda_returns_200(self):
    #     self.HANDLER.handle_request(None, None)
    #     assert 1 == 1

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
