from pyapp.tests.test_batch_processor import BatchProcessorLambdaTestCase

from lambdas.batch_processor.handler import (
        process_shipments, 
        process_carriers,
        process_status_updates
)

from unittest.mock import MagicMock, patch
import pytest
import os
import datetime
import json


class TestSuccess(BatchProcessorLambdaTestCase):

    def test_process_shipments(self):
        with patch(
            "lambdas.batch_processor.handler.execute_many"
        ) as mock_execute:

            content = "shipment_id,order_id,origin,destination,weight_kg,created_at\n"
            content += "s1,o1,Minsk,Warsaw,10.5,2025-01-01T10:00:00"
            
            process_shipments(content)

            mock_execute.assert_called_once()

            sql, values = mock_execute.call_args[0]

            assert len(values) == 1
            assert values[0][0] == "s1"


    def test_process_carriers(self):
        with patch(
            "lambdas.batch_processor.handler.execute_many"
        ) as mock_execute:

            content = "carrier_id,name,email,phone,is_active\n"
            content += "c1,DHL,dhl@test.com,12345,true"

            process_carriers(content)

            mock_execute.assert_called_once()

            sql, values = mock_execute.call_args[0]

            assert values[0][0] == "c1"
            assert values[0][4] is True

    
    def test_process_status_updates(self):
        with patch(
            "lambdas.batch_processor.handler.fetch_all"
        ) as mock_fetch:
            with patch(
                "lambdas.batch_processor.handler.execute_many"
            ) as mock_execute:

                mock_fetch.side_effect = [
                    [("s1",)],
                    [("c1",)]
                ]

                content = "shipment_id,carrier_id,status,location,notes,timestamp\n"
                content += "s1,c1,CREATED,Minsk,test,2025-01-01T10:00:00"

                process_status_updates(content)

                mock_execute.assert_called_once()

                _, values = mock_execute.call_args[0]

                assert values[0][0] == "s1"
                assert values[0][1] == "c1"
                assert values[0][2] == "CREATED"


    def test_invalid_status_skipped(self):
        with patch(
            "lambdas.batch_processor.handler.fetch_all"
        ) as mock_fetch:
            with patch(
                "lambdas.batch_processor.handler.execute_many"
            ) as mock_execute:

                mock_fetch.side_effect = [
                    [("s1",)],
                    [("c1",)]
                ]

                content = "shipment_id,carrier_id,status,location,notes,timestamp\n"
                content += "s1,c1,BAD_STATUS,Minsk,test,2025-01-01T10:00:00"

                process_status_updates(content)

                mock_execute.assert_not_called()

    
    def test_lambda_routes_shipments(self):
        with patch(
            "lambdas.batch_processor.handler.process_shipments"
        ) as mock_process:
            with patch(
                "lambdas.batch_processor.handler.download_s3_object"
            ) as mock_download:

                mock_download.return_value = "content"

                event = {
                    "Records": [
                        {
                            "s3": {
                                "bucket": {
                                    "name": "bucket"
                                },
                                "object": {
                                    "key": "shipments.csv"
                                }
                            }
                        }
                    ]
                }

                result = self.HANDLER.handle_request(event, None)

                assert result["statusCode"] == 200

                mock_process.assert_called_once_with(
                    "content"
                )

