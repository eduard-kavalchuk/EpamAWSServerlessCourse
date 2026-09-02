 # 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task05

# 4. Switch to task05/ directory:
cd task05/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
uv run syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-455/mxhmo8sx/task05" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task05,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAQR5EPT44KZ6E73KZ" \
    --secret-key "cVHcjbABZKNNuMHw6iWxxBjXLgGqXPZwV728CzP+" \
    --session-token "IQoJb3JpZ2luX2VjEAAaDGV1LWNlbnRyYWwtMSJIMEYCIQCNpibUFuXlQUfGdUvz1RBg0N+0sXyAO1iNu3pM14T1egIhAJwIYgL1tCLwD5P/lE8ZPlL/DoCCw5zpaln3uydlPMEwKtECCMn//////////wEQABoMMDM4NDYyNzkxNDgwIgzZm20d8/lt5R0MZaoqpQKu+8GiOBDtMPhUn+6qiH6gzlSU/pbtsvv76sHT6vJEg0rHhwwmnj4gPblIu56yT5JLkGWdLbQJURQbxJHcAkaL00D8E5KzGWGwM32B1Jyq8/XOJBUzmeAhprIRPcJD1db6D3Qw8Wm3D9dtDdCeH4uoq+GIzm5udl/nuSBApUGnbQiL37lNzcAhlcmUP94sLU+OsPzLKRh2o2nIKFbuiS2v2qNX/0D+kN0+LqmVwOjHQONnFji54+tu3jDioAJNFn7ZLS31wmTE220X+GHqC/joJwe65/x7q0A85CJiEreMXaL8ykieOCa8/obL0f/laYlAyxfqkrCSrR0Rf8hYFfWaZHHwsJisMzBXs/1DkMNoP4YgK+xNo4I2gTKtiWs3Pqp+truGTjDemeHUBjqcAXnTlrgvbNH6QO3C0qxDhshOlWfAjvR4BhK1hzHZmxcwRFXkHE3plnYpem8/lB5sonnxMYJdJA5o7thtbpxBvuEvPUuD/uHdTrRHWp7LHN8BOndaPXIA/4+kUMAr2/tybRUnWFMfbjS0SFEXw11YHMQvAaIRENe4oaVZdCqmaKDhi4A7dXeKx5l5QvMatRuJbeU2HqY7JEuWzwWt7A=="
    
# 6. Generate a config that Syndicate will use to access AWS account where project will be deployed:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task05/.syndicate-config-dev"

# 7. Set up the SDCT_CONF environment variable pointing to the folder with syndicate.yml file:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task05/.syndicate-config-dev"

# 8. Generate the DynamoDB resource:
uv run syndicate generate meta dynamodb \
    --resource-name Events \
    --hash-key-name id \
    --hash-key-type S

# 9. Add the following key:value pair to ./task05/deployment_resources.json to "Events" resource.

"table_name": "Events",

# 10. Generate lambda
uv run syndicate generate lambda --name=api_handler --runtime=python

# 11. Specify correct alias for the lambda function (required by task description):
Open .syndicat-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 12. Generate the API Gateway
uv run syndicate generate meta api_gateway \
    --resource-name task5_api \
    --deploy-stage api

# 13. Create the /events resource
uv run syndicate generate meta api_gateway_resource \
    --api-name task5_api \
    --path /events

# 14. Create POST /events
uv run syndicate generate meta api-gateway-resource-method \
    --api-name task5_api \
    --path /events \
    --method POST \
    --integration-type lambda \
    --lambda-name api_handler \
    --authorization-type NONE

# 15. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task05/ folder):
uv run syndicate test    

* Logs can be found in task05/.syndicate-config-dev/logs folder
* In this task Copilot provided tests that test function response and DynamoDB write operation using mocks

# 16. Build the artifacts of the application and create a bundle:
uv run syndicate build   
  
* In case of build errors of failed tests you will get an error message.


# 17. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose  
  
* In case of errors see a log in ./task04/.syndicate-condif-dev/ directory


# 18. Verify that lambda function exists:
aws lambda list-functions \
    --query 'Functions[].FunctionName' \
    --output table

# 19. Check that API gateway exists:
aws apigateway get-rest-apis \
    --query 'items[*].[id,name]' \
    --output table
    
* In my case API ID is ptp6fu8g1g . It will be used in commands that follow below.

# 20. Verify that the /events POST resource is configured correctly:
aws apigateway get-resources --rest-api-id ptp6fu8g1g 


# 21. Verify that Events table of DynamoDB exists:
aws dynamodb list-tables

* ATTENTION! Correct table name will be cmtr-mxhmo8sx-Events!

# 22. Check the content of cmtr-mxhmo8sx-Events:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Events

# 23. Send the following POST request AND THEN DEBUG IN STEP #24!
curl -v -X POST \
  "https://ptp6fu8g1g.execute-api.eu-west-1.amazonaws.com/api/events" \
  -H "Content-Type: application/json" \
  -d '{
        "principalId": 1,
        "content": {
          "name": "John",
          "surname": "Doe"
        }
      }'

# 24. IN CASE OF ERROR get error messages from CLoudFront:
aws logs tail /aws/lambda/cmtr-mxhmo8sx-api_handler --follow


# 25. Check the content of cmtr-mxhmo8sx-Events:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Events
