from pyapp.tests.test_batch_processor import BatchProcessorLambdaTestCase


class TestSuccess(BatchProcessorLambdaTestCase):

    def test_success(self):
        result = self.HANDLER.handle_request(dict(), None)

        assert result["statusCode"] == 200


