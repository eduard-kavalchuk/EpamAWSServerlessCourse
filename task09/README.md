# 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task09

# 4. Switch to task08/ directory:
cd task09/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
uv run syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-3013/mxhmo8sx/task09" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task09,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAS5G2US4HO7XVOUC7" \
    --secret-key "6Zp4xkod7TtE2UDhuWR9xInJLrMORWp8eqgxLdIR" \
    --session-token "IQoJb3JpZ2luX2VjEG8aDGV1LWNlbnRyYWwtMSJHMEUCIFHZ7r9i3n6yMymjJx0F8KFWoC6XkNxpkBa7JDyUJyWHAiEApcdDP/9TH2ICiLKuYp3KSZUPubllLXgdQhCYbRqe0G8qyAIIOBAAGgwyMDAxNzQ1MDc3OTAiDPWFuXay/yIEDj+02yqlAslcz5YRsp5axwr7K2Cf65EHvHP45XDWzoIfK0Rzzd+vtVRGlZFVUSokKK/fpZ/ie3UaTN2bdQNfDfKUqmX3ykzP82n7daHJzLOSMSOg2Hkg38qoEu5HRwkLbYrA7Ix65C85fp7pHD1yZflGFWJIGBlgoNZHLjcDX5XyJBdd2KIVPncGV58XjHkas9mDx6KelwQbj4jp+wUWDFPqm7zDfhUv9PuoxoI2/eOWkf+iNiy53PEiRkhcwxQI6knWHasYST2cSiXVRsZDhUD0cRc4HCrz1Q9m9cmjPz0NSCKTvcbI8x2XvioFqeav0NuFUxPtVXAXm99kbjDENHAauhIrmQ8oidTuvRO27jX9SLUvbCP64IS1skvX5+PVSGZO3mhpVyiKP9NJMIu8+dQGOp0BkOlInkptviGYnYPAQT/bcDAa31Zlp+nR1P+DNV8/VLCl/C8FDDawNp+bKQnakeWDj1m70DfmNulNBarbAd9QjaysbfKcPWAEoOs2d0Ht1VqP3RjkuSLRxL+AON466TwfEVt5Mc0Q7stDFpoNIupo9NC4nrziuJ2QeA807InPojeQFuo3xJYZpee7dIi4N3vLiKUbAFe0s9SqK4pnHQ=="

# 6. Generate a config that Syndicate will use to access AWS account where project will be deployed:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task09/.syndicate-config-dev"

# 7. Generate lambda
uv run syndicate generate lambda --name=api_handler --runtime=python

# 8. Specify correct alias for the lambda function (required by task description):
Open .syndicate-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 9. Generate lambda layer:
uv run syndicate generate lambda-layer --name=weather_sdk --runtime=python

# 10. Add the HTTP dependency: inside layers/weather_sdk/requirements.txt put:
requests

# 11. Put SDK implementation into client.py:

import requests

class OpenMeteoClient:
    URL = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=52.52"
        "&longitude=13.41"
        "&current=temperature_2m,wind_speed_10m"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    def get_weather(self):
        response = requests.get(self.URL, timeout=10)
        response.raise_for_status()
        return response.json()

# 12. Add the following dependency to lambda_config.json:
"layers": [
        "weather_sdk"
    ],

# 14. Implement your lambda function.

# 15. Test:
uv run syndicate test 

# 16. Build the artifacts of the application and create a bundle:
uv run syndicate build 

# 17. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose 



# ------- [ Testing the deploy ] --------------------------------------

# 1. Verify the Layer was deployed:
aws lambda list-layers

* "LayerName": "cmtr-mxhmo8sx-weather_sdk"
* "LayerArn": "arn:aws:lambda:eu-west-1:970378220557:layer:cmtr-mxhmo8sx-weather_sdk"

# 2. To inspect the specific layer:
aws lambda list-layer-versions \
    --layer-name cmtr-mxhmo8sx-weather_sdk

* "Version": <integer>

# 3. List your lambda function:
aws lambda list-functions \
  --query "Functions[?contains(FunctionName,'api_handler')].FunctionName"

* cmtr-mxhmo8sx-api_handler

# 4. Verify your Lambda configuration:
aws lambda get-function-configuration \
    --function-name cmtr-mxhmo8sx-api_handler

* Make sure layer was attached:
"Layers": [
    {
        "Arn": "arn:aws:lambda:eu-west-1:970378220557:layer:cmtr-mxhmo8sx-weather_sdk:1",
        "CodeSize": 2644
    }
]

# 5. Verify Function URL:
aws lambda get-function-url-config \
    --function-name cmtr-mxhmo8sx-api_handler:learn

* ATTENTION! Make sure you use ":learn" in call above! Otherwise, an exception will be returnedQ

* "FunctionUrl": "https://atjowniizimtu3vj33spqwr52a0gccgw.lambda-url.eu-west-1.on.aws/"

# 6. Test correct endpoint:
curl https://atjowniizimtu3vj33spqwr52a0gccgw.lambda-url.eu-west-1.on.aws/weather

* This one should return correct resonse
* In case of failure see instructions below on how to debug

# 7. Test incorrect endpoint:
curl https://atjowniizimtu3vj33spqwr52a0gccgw.lambda-url.eu-west-1.on.aws/incorrect




* In case of failure see instructions below on how to debug

# ---------- [ Debugging Internal Server Error ] -----------------------------

aws logs tail \
/aws/lambda/cmtr-mxhmo8sx-api_handler \
--since 10m
