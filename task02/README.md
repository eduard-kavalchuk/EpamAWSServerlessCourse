# 1. Create a project on github
https://github.com/eduard-kavalchuk/EpamAWSServerlessCourse.git

# 2. Clone the repo:
git clone https://github.com/eduard-kavalchuk/EpamAWSServerlessCourse.git

# 3. cd to dir
cd EpamAWSServerlessCourse

# 4. Initialize uv in a cloned directory
uv init --bare

# 5. Create and activate the virtual environment
uv venv

# 6. Activate the virtual environment
source .venv/bin/activate

# 7. Add new dependencies
uv add aws-syndicate

# 8. (Optional) Add development dependencies
uv add --dev pytest black

# 9. (Optional) Sync dependencies from pyproject.toml
uv sync

# 10. Create a syndicated project
uv run syndicate generate project --name task02

# 11. Switch to task02 directory:
cd task02/

# 12. Generate a config that Syndicate will use to access AWS account where project will be deployed

Copy and paste full command from "Credentials":

uv run syndicate generate config --name "dev"


# 13. Set up the SDCT_CONF environment variable pointing to the folder with syndicate.yml file:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task02/.syndicate-config-dev"

# 14. Generate lambda
uv run syndicate generate lambda --name=hello_world --runtime=python

# 15. To enable  Function URL for your lambda function add the following setting to your task02/pyapp/src/lambdas/hello_world/lambda_config.json file:
{
    ...
    "url_config": {
    "auth_type": "AWS_IAM"
    }
}

--- Please note that giving "NONE" instead of "AWS_IAM" will not allow anyone make requests to URL!


# 16. Create the bundle bucket in S3:
uv run syndicate create-deploy-target-bucket

# 17. Specify correct alias for the lambda function (required by task description):
Open .syndicat-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 18. Cover your lambda function with tests

# 19. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task02/ folder):
uv run syndicate test    # logs can be found in task02/.syndicate-config-dev/logs folder

# 20. Build the artifacts of the application and create a bundle:
uv run syndicate build     # In case of build errors of failed tests you will get an error message.

# 21. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy

# 22. To get function's URL run the following command:
aws lambda get-function-url-config --function-name cmtr-mxhmo8sx-hello_world:learn
-- Please note that what is called here is not function itself but its alias "learn". In this task function itself has no Function URL.
-- Here is the response on this command:
{
    "FunctionUrl": "https://q4lxyt4rbiyej6bxl466x55fuq0jfkzc.lambda-url.eu-west-1.on.aws/",
    "FunctionArn": "arn:aws:lambda:eu-west-1:536697226993:function:cmtr-mxhmo8sx-hello_world:learn",
    "AuthType": "NONE",
    "CreationTime": "2026-08-25T04:24:42.237129342Z",
    "LastModifiedTime": "2026-08-25T04:24:42.237129342Z",
    "InvokeMode": "BUFFERED"
}

# 23. Test by sending requests to this function with curl:
curl https://q4lxyt4rbiyej6bxl466x55fuq0jfkzc.lambda-url.eu-west-1.on.aws/
-- Response:
{"statusCode": 400, "message": "Bad request syntax or unsupported method. Request path: /. HTTP method: GET"}

curl https://q4lxyt4rbiyej6bxl466x55fuq0jfkzc.lambda-url.eu-west-1.on.aws/hello
-- Response:
{"statusCode": 200, "message": "Hello from Lambda"}

curl -X POST https://q4lxyt4rbiyej6bxl466x55fuq0jfkzc.lambda-url.eu-west-1.on.aws/hello \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

-- Response:
{"statusCode": 400, "message": "Bad request syntax or unsupported method. Request path: /hello. HTTP method: POST"}


# 24. Push your solution to github:
git push

