import os

from pyapp.tests.test_processor import ProcessorLambdaTestCase
from unittest.mock import Mock, patch

os.environ["EVENTS_TABLE"] = "Weather"


class TestSuccess(ProcessorLambdaTestCase):

    def test_weather_get(self):
        """
        Verify response
        """
        with patch(
            "lambdas.processor.handler.boto3.resource"
        ) as mock_resource:
            
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table

            response = self.HANDLER.handle_request(None, None)

            print(response)

            self.assertEqual(response["statusCode"], 200)


    def test_weather_db_write(self):
        """
        Verify exactly what is written to DynamoDB
        """
        with patch(
            "lambdas.processor.handler.boto3.resource"
        ) as mock_resource:
            
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table

            self.HANDLER.handle_request(None, None)

            mock_table.put_item.assert_called_once()
            saved_item = mock_table.put_item.call_args.kwargs["Item"]

            self.assertIn("id", saved_item)
            self.assertIn("forecast", saved_item)
            self.assertIn("elevation", saved_item["forecast"])
