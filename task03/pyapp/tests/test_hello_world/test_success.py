import json

from pyapp.tests.test_hello_world import HelloWorldLambdaTestCase


class TestSuccess(HelloWorldLambdaTestCase):

    def test_success(self):
        response = self.HANDLER.handle_request(dict(), dict())
        expected_response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'statusCode': 200,
                'message': 'Hello from Lambda'
            })
        }

        self.assertEqual(response, expected_response)

