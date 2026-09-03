import os

from unittest.mock import MagicMock, patch
from pyapp.tests.test_audit_producer import AuditProducerLambdaTestCase

os.environ["AUDIT_TABLE"] = "Audit"


class TestSuccess(AuditProducerLambdaTestCase):

    def test_insert_event(self):
        with patch(
            "lambdas.audit_producer.handler.boto3.resource"
        ) as mock_resource:
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table

            event = {
                "Records": [
                    {
                        "eventName": "INSERT",
                        "dynamodb": {
                            "NewImage": {
                                "key": {"S": "CACHE_TTL_SEC"},
                                "value": {"N": "3600"}
                            }
                        }
                    }
                ]
            }

            response = self.HANDLER.handle_request(event, None)

            assert response["statusCode"] == 200

            mock_table.put_item.assert_called_once()

            inserted_item = (
                mock_table.put_item.call_args.kwargs["Item"]
            )

            assert inserted_item["itemKey"] == "CACHE_TTL_SEC"

            assert inserted_item["newValue"] == {
                "key": "CACHE_TTL_SEC",
                "value": 3600
            }


    def test_modify_event(self):
        with patch(
            "lambdas.audit_producer.handler.boto3.resource"
        ) as mock_resource:
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table

            event = {
                "Records": [
                    {
                        "eventName": "MODIFY",
                        "dynamodb": {
                            "OldImage": {
                                "key": {"S": "CACHE_TTL_SEC"},
                                "value": {"N": "3600"}
                            },
                            "NewImage": {
                                "key": {"S": "CACHE_TTL_SEC"},
                                "value": {"N": "1800"}
                            }
                        }
                    }
                ]
            }

            response = self.HANDLER.handle_request(event, None)

            assert response["statusCode"] == 200

            mock_table.put_item.assert_called_once()

            item = mock_table.put_item.call_args.kwargs["Item"]

            assert item["itemKey"] == "CACHE_TTL_SEC"
            assert item["updatedAttribute"] == "value"
            assert item["oldValue"] == 3600
            assert item["newValue"] == 1800


    def test_empty_records(self):
        with patch(
            "lambdas.audit_producer.handler.boto3.resource"
        ) as mock_resource:
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table

            event = {"Records": []}

            response = self.HANDLER.handle_request(event, None)

            assert response["statusCode"] == 200
            