from pyapp.tests.test_sqs_handler import SqsHandlerLambdaTestCase


class TestSuccess(SqsHandlerLambdaTestCase):

    def test_success(self):
            response = self.HANDLER.handle_request(dict(), dict())

            expected_response = {
                "statusCode": 200,
                "processedMessages": 0
            }
    
            self.assertEqual(response, expected_response)

