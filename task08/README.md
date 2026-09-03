# 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task08

# 4. Switch to task08/ directory:
cd task08/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
uv run syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-6109/mxhmo8sx/task08" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task08,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAS5G2US4HCZJANGZS" \
    --secret-key "9XExN5T3FsmoWyHvzeV2WScCsIbOxzXqGy8zuVex" \
    --session-token "IQoJb3JpZ2luX2VjEBoaDGV1LWNlbnRyYWwtMSJHMEUCIFVaPIRAWTjItAsUMiDO8ZFDsM1nDjnBRwCo3/KbBcOtAiEA/VgeAh5Xzzp+R/SIRd/tMYej17D4TTG2SXxYXywfecoq0QII4///////////ARAAGgwyMDAxNzQ1MDc3OTAiDA3q168a2MwA20d5bCqlAgQ1ZxEzzLI9ErVLBptn1V1G1hjBmydZ+sNFkFZMRBtCUHt8UE6h2jOOafTy/6jqpj/II5SISKDX3dJqjUnJTf2MgpL1ja7SP7Kued1EarKFtOFPoWwI0LlYfGLoyQpCEv1Ff2JRTT1vzVAwAQ/rpL44HZMP1G+gL+fzJK2WLpI3iMRMk3Jf/FRqs30lnvhDBGIoyufCwVowlK3qZfQXRcC0FBysWDFxdeMuv8Bh5xS/Uq/3foCTPpSHH+Eh6sGzbGg08++UR0Y0MImLkwJ3c/+QJ/QimciAY/9J9ydkfG/ZzWSrSsYNEFecWLsA5SXL2HyoiOWr7CQJil9uJSjG1xEXgAABRfUAQEgi7smcaZCp4WIu57Os96MmHJaMCKl5awjqkp+8MOz15tQGOp0BKkWXHh56q9tUrRhPSOoSD129izsDzwi9SZxN1fJTJZDy2199hns5AcPcv3w8yZjvIF1pTEzrcNwSiSLVU96RznvLRuaznWDE1FQqMHs4XXiwf6LV/m71PVNiiiDGShlDcfPiTN9qjkOvbZfQ3sFPs5stej6Jeb4wKVMVjnK7Pyz13Lp+Wn6HtcEKHsawv12Pyx2cM2Kff4ztjAIwaQ=="

# 6. Generate a config that Syndicate will use to access AWS account where project will be deployed:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task08/.syndicate-config-dev"

# 7. Generate lambda
uv run syndicate generate lambda --name=uuid_generator --runtime=python

# 8. Specify correct alias for the lambda function (required by task description):
Open .syndicate-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 9. Generate S3 Bucket Resource Description:
uv run syndicate generate meta s3-bucket --resource-name uuid-storage

# 10. Generate CloudWatch Rule Description:
uv run syndicate generate meta cloudwatch-event-rule  \
    --resource-name=uuid_trigger --rule-type=schedule

#### Side note #########################
For instance, we want to create a custom role and policy attached to it.
If we are unsure of syntax we can create custom role and policy with the following commands:


# 11. Test:
uv run syndicate test 

# 12. Build the artifacts of the application and create a bundle:
uv run syndicate build 

# 13. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose 

# 14. List you lambda:
aws lambda list-functions \
  --query "Functions[?contains(FunctionName,'uuid_generator')].FunctionName"

* cmtr-mxhmo8sx-uuid_generator


# 15. Get details:
aws lambda get-function-configuration \
  --function-name cmtr-mxhmo8sx-uuid_generator

* Verify:
    function exists
    runtime is Python 3.10
    environment variable BUCKET_NAME is present


# 16. Verify there is a bucket:
aws s3 ls

* cmtr-mxhmo8sx-uuid-storage


# 17. List EventBridge Rules
aws events list-rules \
  --name-prefix cmtr-mxhmo8sx
  
  
# 18. Inspect the rule:
aws events describe-rule \
  --name cmtr-mxhmo8sx-uuid_trigger

* Must be "rate(1 minute)"

# 19. Check targets:
aws events list-targets-by-rule \
  --rule cmtr-mxhmo8sx-uuid_trigger

* ARN must point to the lambda function:
arn:aws:lambda:eu-west-1:242201307208:function:cmtr-mxhmo8sx-uuid_generator:learn


# 20. Verify Lambda Permission for EventBridge:
aws lambda get-policy \
  --function-name cmtr-mxhmo8sx-uuid_generator:learn

* You should see a statement granting:
events.amazonaws.com


# 21. Invoke the Lambda Manually. Don't wait a minute. Test immediately:
aws lambda invoke \
  --function-name cmtr-mxhmo8sx-uuid_generator \
  response.json

* response.json must contain:
"statusCode": 200


# 22. Check CloudWatch Logs:
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/cmtr-mxhmo8sx-uuid_generator
  
  
# 23. Get recent streams:
aws logs describe-log-streams \
  --log-group-name /aws/lambda/cmtr-mxhmo8sx-uuid_generator \
  --order-by LastEventTime \
  --descending


# 24. Verify Files Are Written to S3. List objects:
aws s3 ls s3://cmtr-mxhmo8sx-uuid-storage/

* There must be objects written each minute
