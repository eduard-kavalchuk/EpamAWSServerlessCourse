from pyapp.tests.test_batch_processor import BatchProcessorLambdaTestCase


class TestSuccess(BatchProcessorLambdaTestCase):

    def test_success(self):
        self.assertEqual(self.HANDLER.handle_request(dict(), dict()), 200)

