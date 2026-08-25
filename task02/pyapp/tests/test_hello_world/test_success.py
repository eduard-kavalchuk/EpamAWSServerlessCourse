import json

from pyapp.tests.test_hello_world import HelloWorldLambdaTestCase


class TestSuccess(HelloWorldLambdaTestCase):

    def test_success(self):
        event = {
            'rawPath': '/hello',
            'requestContext': {
                'http': {
                    'method': 'GET'
                }
            }
        }

        context = {}

        response = self.HANDLER.handle_request(event, context)
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

    def test_fail_wrong_resource(self):
        path = '/helloworld'
        method = 'GET'

        event = {
            'rawPath': path,
            'requestContext': {
                'http': {
                    'method': method
                }
            }
        }

        context = {}

        response = self.HANDLER.handle_request(event, context)

        expected_response = {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'statusCode': 400,
                'message': f'Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}'
             })
        }

        self.assertEqual(response, expected_response)

    def test_fail_wrong_request(self):
        path = '/hello'
        method = 'POST'

        event = {
            'rawPath': path,
            'requestContext': {
                'http': {
                    'method': method
                }
            }
        }

        context = {}

        response = self.HANDLER.handle_request(event, context)
        expected_response = {
           'statusCode': 400,
           'headers': {
               'Content-Type': 'application/json'
           },
           'body': json.dumps({
               'statusCode': 400,
               'message': f'Bad request syntax or unsupported method. Request path: {path}. HTTP method: {method}'
            })
        }

        self.assertEqual(response, expected_response)

