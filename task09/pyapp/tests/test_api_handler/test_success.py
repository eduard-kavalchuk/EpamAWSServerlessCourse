from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase
from unittest.mock import patch


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_weather_get(self):
        with patch("lambdas.api_handler.handler.OpenMeteoClient" ) as mock_client:
            mock_client.return_value.get_weather.return_value = {
                "temperature": 20
            }

        event = {
            "rawPath": "/weather",
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }

        response = self.HANDLER.handle_request(event, None)

        print(response)

        self.assertEqual(response["statusCode"], 200)

    def test_bad_request(self):
        event = {
            "rawPath": "/unknown",
            "requestContext": {
                "http": {
                    "method": "GET"
                }
            }
        }

        response = self.HANDLER.handle_request(event, None)

        self.assertEqual(response["statusCode"], 400)