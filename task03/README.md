# 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task03

# 4. Switch to task02 directory:
cd task03/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
Execute the following command with correct credentials:

syndicate generate config --name "dev"


# 6. Set up the SDCT_CONF environment variable pointing to the folder with syndicate.yml file:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task03/.syndicate-config-dev"

# 7. Generate lambda
uv run syndicate generate lambda --name=hello_world --runtime=python

# 8. Specify correct alias for the lambda function (required by task description):
Open .syndicat-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 9. Implement lambda function

# 10. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task03/ folder):
uv run syndicate test    # logs can be found in task03/.syndicate-config-dev/logs folder

# 11. Generate API Gateway metadata
syndicate generate meta api-gateway --resource-name task3_api --deploy-stage api

# 12. Open ./task03/deployment_resources.json file and specify "resources" for "task3_api" gateway:
{
  "api_name": "task3_api",
  "stage": "api",
  "resources": {
    "/hello": {
      "GET": {
        "lambda": "hello_world"
      }
    }
  }
}

# 13. Build the artifacts of the application and create a bundle:
uv run syndicate build     # In case of build errors of failed tests you will get an error message.

# 14. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose    # in case of errors see a log in ./task03/.syndicate-condif-dev/ directory

WARNING!! If a deploy was unsuccessful first do the following:
uv run syndicate clean

and then 

uv run syndicate build

and then

uv run syndicate deploy


WARNING!! Be aware that after deploy the sandbox credentials (the ones that were used in Step 5 to generate the project) go missing somehow and you need to re-export the following envs:

export AWS_REGION=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_SESSION_TOKEN=

# 15. Test the URL:
Method 1. Use Management Console:
a) Go to Management Console > API Gateway > APIs > <your API> > Stages
b) Find the URL and test it with /hello resource

Method 2. USE AWS CLI:
API_ID=$(aws apigateway get-rest-apis \
  --query "items[?name=='cmtr-mxhmo8sx-task3_api'].id | [0]" \
  --output text)

URL="https://${API_ID}.execute-api.eu-west-1.amazonaws.com/api/hello"

curl $URL

# 16. Push your solution to github:
git push

