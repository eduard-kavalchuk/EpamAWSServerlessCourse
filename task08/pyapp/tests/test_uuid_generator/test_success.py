import os
from unittest.mock import Mock, patch

from pyapp.tests.test_uuid_generator import UuidGeneratorLambdaTestCase

os.environ["BUCKET_NAME"] = "uuid-storage"


class TestSuccess(UuidGeneratorLambdaTestCase):

    def test_success(self):
        with patch("lambdas.uuid_generator.handler.s3" ) as mock_s3:
            response = self.HANDLER.handle_request(dict(), dict())

            assert response["statusCode"] == 200

            mock_s3.put_object.assert_called_once()

            args = mock_s3.put_object.call_args.kwargs

            assert args["Bucket"] == "uuid-storage"
            assert args["ContentType"] == "application/json"

