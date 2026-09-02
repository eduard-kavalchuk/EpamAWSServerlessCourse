 # 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task04

# 4. Switch to task04 directory:
cd task04/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-1378/mxhmo8sx/task04" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task04,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAW5WU5J2HYPH4PPJS" \
    --secret-key "SB/nW1fywQ+EahZWNR1eaNTG4dzuh1ru9qv8bjLT" \
    --session-token "IQoJb3JpZ2luX2VjEP3//////////wEaDGV1LWNlbnRyYWwtMSJIMEYCIQDjRJ311ln9htR7Fm5DcQecJs/JHr8WYrL4g6LCYaupdQIhAIhdou4JfFwyPjjjK3+WPGvTmsxh/PR+RIiFV6qgncZkKtECCMb//////////wEQABoMNDc2MTE0MTQ0OTExIgxr6QFy8TO0YVgxDhEqpQIVZcq3wtjs3ur4MDVj+UOxqXIn2YkOZmlq/EeGl3ZltOosppkQF/E6+aIRMHzM4sD2DQdg+CInYJx8UpO3VpR6TRaVwx/qSdpHONY+ee2cM1nenYoSEch8IOhJRgP2AFkbyRYPWf3zEpLt94jQYXd9POox33aNqwXCFEL3+7oFZS75/3bdykeiDnpSoY/qjs8X6YLC/ko2V6tC+klaV2lxHV2aObwXRI7+dD5k60VjKz3IB5xzh1xJAytpAzLJJriYv8EjCgA6vPJmSVNvWBbzllQTp33Vaci4vz0D4BcEPFvedWqW7dOQYeB9kYR1dCN9dEV7NBEM9v7b6NEiAviQbmohxLLRnUXrovxlcJcQJjuOJRr3Sf+A4GelgcIRRLJbtYJqNTD+s+DUBjqcAU8QUNBEFzlF5fzKr112aVuvEMBP/3akNWLb0meU6G4fw7zFx9mClHtfLX3SpVjOgexSN6lAKW9hqgUPKj27DyZK4JR36RAP7B8cL2+fGAo+1zYnHFmKrVNrjGkuyxkjooylRAxo9cUrM9sidGhKBOXKCNQnEBYPLLGFSqBjEgN/TusZIoi3O19gFPRRLmhJ5yrm8QSyI+n7Wg8trg=="

# 6. Set up the SDCT_CONF environment variable pointing to the folder with syndicate.yml file:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task04/.syndicate-config-dev"

# 7. Generate lambda
uv run syndicate generate lambda --name=sqs_handler --runtime=python

# 8. Specify correct alias for the lambda function (required by task description):
Open .syndicat-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 9. Generate SQS Queue Resource in Meta:
uv run syndicate generate meta sqs-queue --resource-name=async_queue

# 10. Modify lambda_config.json as follows to allow lambda to be triggered by SQS:
{
  "version": "1.0",
  "name": "sqs_handler",
  "func_name": "handler.lambda_handler",
  "resource_type": "lambda",
  "iam_role_name": "sqs_handler-role",
  "runtime": "python3.10",
  "memory": 128,
  "timeout": 100,
  "lambda_path": "lambdas/sqs_handler",
  "dependencies": [
    {
      "resource_name": "async_queue",
      "resource_type": "sqs_queue"
    }
  ],
  "event_sources": [
    {
      "resource_type": "sqs_trigger",
      "target_queue": "async_queue",
      "batch_size": 10
    }
  ],
  "env_variables": {},
  "publish_version": true,
  "alias": "${lambdas_alias_name}",
  "url_config": {},
  "ephemeral_storage": 512,
  "logs_expiration": "${logs_expiration}",
  "tags": {}
}

# 11. Implement your lambda to print SQS messages to CloudFront.

# 12. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task04/ folder):
uv run syndicate test    

* Logs can be found in task04/.syndicate-config-dev/logs folder


# 13. Add the following permissions to "lambda-basic-execution" resource in ./task04/deployment_resources.json:
"sqs:ReceiveMessage",
"sqs:DeleteMessage",
"sqs:GetQueueAttributes",
"sqs:ChangeMessageVisibility",

# 14. Build the artifacts of the application and create a bundle:
uv run syndicate build   
  
* In case of build errors of failed tests you will get an error message.

# 15. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose  
  
* In case of errors see a log in ./task04/.syndicate-condif-dev/ directory

# 16. Discover exact function name:
aws lambda list-functions \
    --query 'Functions[].FunctionName' \
    --output table

# 17. Run the following command to make sure there is mapping:
aws lambda list-event-source-mappings \
    --function-name cmtr-mxhmo8sx-sqs_handler:learn

* Notice :learn suffix! Without it the mapping will be empty!

# 18. Get the <queue-url>:
aws sqs list-queues
    
# 19. Get <account-id>:
aws sts get-caller-identity

# 20. Send message to the queue (paste <queue-url> without ""):
aws sqs send-message \
    --queue-url <queue-url> \
    --message-body "Hello from SQS"

* Example:
aws sqs send-message \
    --queue-url https://sqs.eu-west-1.amazonaws.com/476114144911/cmtr-mxhmo8sx-async_queue \
    --message-body "Hello from SQS"

# 21. Watch the lambda logs:
aws logs tail /aws/lambda/cmtr-mxhmo8sx-sqs_handler --follow


# ------------ [ SNS handler part] ---------------------------------------------

# 22. Generate lambda
uv run syndicate generate lambda --name=sns_handler --runtime=python

# 23. Generate SNS Queue Resource in Meta:
uv run syndicate generate meta sns-topic --resource-name=lambda_topic --region=eu-west-1

# 24. Modify lambda_config.json as follows to allow lambda to be triggered by SQS:
{
  "version": "1.0",
  "name": "sns_handler",
  "func_name": "handler.lambda_handler",
  "resource_type": "lambda",
  "iam_role_name": "sns_handler-role",
  "runtime": "python3.10",
  "memory": 128,
  "timeout": 30,
  "lambda_path": "lambdas/sns_handler",
  "dependencies": [{
      "resource_name": "lambda_topic",
      "resource_type": "sns_topic"
    }
  ],
  "event_sources": [{
      "resource_type": "sns_topic_trigger",
      "target_topic": "lambda_topic"
    }
  ],
  "env_variables": {},
  "publish_version": true,
  "alias": "${lambdas_alias_name}",
  "url_config": {},
  "ephemeral_storage": 512,
  "logs_expiration": "${logs_expiration}",
  "tags": {}
}

# 25. Implement your lambda to print the content of the SNS message to CloudWatch Logs.

# 26. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task04/ folder):
uv run syndicate test

* Logs can be found in task04/.syndicate-config-dev/logs folder

# 27. Build the artifacts of the application and create a bundle:
uv run syndicate build   
  
* In case of build errors of failed tests you will get an error message.

# 28. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose  
  
* In case of errors see a log in ./task04/.syndicate-condif-dev/ directory

# 29. Get the list of lambda functions and notice the one which processes SNS:
aws lambda list-functions \
    --query 'Functions[].FunctionName' \
    --output table

* cmtr-mxhmo8sx-sns_handler

# 30. Check the Lambda triggers in the console or list Lambda permissions:
aws lambda get-policy \
    --function-name cmtr-mxhmo8sx-sns_handler:learn

# 31. Check the SNS subscriptions and make sure that there is a subscription whose endpoint is the Lambda ARN:
aws sns list-subscriptions

# 32. Get the Topic ARN:
aws sns list-topics

* arn:aws:sns:eu-west-1:476114144911:cmtr-mxhmo8sx-lambda_topic

# 33. Publish a message:
aws sns publish \
    --topic-arn arn:aws:sns:eu-west-1:476114144911:cmtr-mxhmo8sx-lambda_topic \
    --message "Hello from SNS"
    
# 34. Watch the lambda logs:
aws logs tail /aws/lambda/cmtr-mxhmo8sx-sns_handler --follow

# 35. Commit and push.

