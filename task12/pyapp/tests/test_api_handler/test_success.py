from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import Mock, patch

import os

os.environ["TABLES_TABLE"] = "Tables"
os.environ["RESERVATIONS_TABLE"] = "Reservations"
os.environ["USER_POOL_NAME"] = "simple-booking-userpool"


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_success(self):
        event = {
            "resource": "This is a resource",
            "path": "This is path",
            "httpMethod": "This is httpMethod"
        }

        response = self.HANDLER.handle_request(event, None)

        self.assertEqual(response["statusCode"], 200)

