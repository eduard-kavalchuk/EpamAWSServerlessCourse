
from pyapp.tests.test_api_handler import ApiHandlerLambdaTestCase

import json
from unittest.mock import Mock, patch


class TestSuccess(ApiHandlerLambdaTestCase):

    def test_success(self):
        with patch(
            "lambdas.api_handler.handler.boto3.resource"
        ) as mock_resource:
            
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table

            event = {
                "principalId": 1,
                "content": {
                    "name": "John",
                    "surname": "Doe"
                }
            }

            response = self.HANDLER.handle_request(event, None)

            self.assertEqual(response["statusCode"], 201)
            self.assertEqual(response["event"]["principalId"], 1)
            self.assertEqual(response["event"]["body"]["name"], "John")
            print(response["event"])

            mock_table.put_item.assert_called_once()

            # Verify exactly what is written to DynamoDB
            saved_item = mock_table.put_item.call_args.kwargs["Item"]

            self.assertEqual(saved_item["principalId"], 1)
            self.assertEqual(saved_item["body"]["name"], "John")
            self.assertIn("id", saved_item)
            self.assertIn("createdAt", saved_item)
