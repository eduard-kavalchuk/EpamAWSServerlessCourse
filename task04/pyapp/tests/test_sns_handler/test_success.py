from pyapp.tests.test_sns_handler import SnsHandlerLambdaTestCase


class TestSuccess(SnsHandlerLambdaTestCase):

    def test_success(self):
            response = self.HANDLER.handle_request(dict(), dict())

            expected_response = {
                "statusCode": 200,
            }
    
            self.assertEqual(response, expected_response)

