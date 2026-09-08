from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import Mock, patch

import os

os.environ["TABLES_TABLE"] = "Tables"
os.environ["RESERVATIONS_TABLE"] = "Reservations"


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_success(self):
        response = self.HANDLER.handle_request(None, None)

        self.assertEqual(response["statusCode"], 200)

