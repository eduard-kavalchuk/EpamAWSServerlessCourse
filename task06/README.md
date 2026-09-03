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
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-3158/mxhmo8sx/task06" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task06,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIARHQBNKAPHJD7LS3L" \
    --secret-key "KSDjF/MiZX04b92yie+/yungblBWMzeeL6BUh2ql" \
    --session-token "IQoJb3JpZ2luX2VjEA4aDGV1LWNlbnRyYWwtMSJHMEUCIDl63GNEy4Z0UXm5F91OAnQdyEVTjk0nsF99pdV0ToNvAiEAhDvrM2p/3DFIOsTRwVOgdJQp6fTrWVFlHE5jGDQYJpkq0QII1///////////ARAAGgwwODQ4Mjg1NzM3MjYiDGbnazG4VfNgi2KceSqlArQAvv38o7FoOAGq0x1he9abkIriJcqHViSua0lTDPLoHVUIK/FQaiD8yHSyBmHzJAR7iKWpB9p1W/aE6/VAP07H+sebPbGx8nlDfPYL+F8oSkJmpT1n2iVCBr51pCtIZOipIJhoTil1bxY4tI6nIifbb/xGlEUKc8Lvg0pRDh9WX0P59mFxnfyHTxjUjQtlkoWcffaIcO8R1oaXEqC97zjRJC5DhdlYTd1TzNd+a1ucrKqbiKsb15AgSdRCqw0fR5n86KHJ3EiCZmZKW4xvGaD8SKT1Yhp0rZR+wNVqq5Q4Nfyb2aPm/2gvApvWn12hjRBcxqfrVCVDl6hKBIBEy0JTcaqh5/cq7SmjZdaeyddU6Rj7cEeMfEI5dTOPD8wV6+0P7+FtMP6a5NQGOp0BZdeKTvqJnpnx1Ht+y3ocDMs5bZ2aY7YSxmhp6pJ73fngwgUQt7J+YanWajgQh/LGPNQBpomxc0lYiHHJ2YRgOfx58Qt/C5Wrsc+9xCTVqzcyBOvnRaIBLBSW4HCJ7uuS597aR8HKIazvagS876Q0LMMKF9XCpoI5hu1+5AlyLxaHA5C0NSQt6ZZayzXSUXBcXVmC5GRINMzp2/zYRg=="
    
# 6. Generate a config that Syndicate will use to access AWS account where project will be deployed:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task05/.syndicate-config-dev"

# 7. Generate lambda
uv run syndicate generate lambda --name=audit_producer --runtime=python

# 8. Specify correct alias for the lambda function (required by task description):
Open .syndicate-config-dev/syndicate_aliases.yml file and change "lambdas_alias_name" to "learn".

# 9. Generate the DynamoDB resource named "Configuration":
uv run syndicate generate meta dynamodb \
    --resource-name Configuration \
    --hash-key-name key \
    --hash-key-type S

# 10. Add the following key:value pair to ./task06/deployment_resources.json to "Configuration" resource.

"table_name": "Configuration"

# 11. Generate the DynamoDB resource named "Audit":
uv run syndicate generate meta dynamodb \
    --resource-name Audit \
    --hash-key-name key \
    --hash-key-type S

# 12. Add the following key:value pair to ./task06/deployment_resources.json to "Audit" resource.

"table_name": "Audit"

# 13. Run the tests (you can run command below from any folder since syndicate knows how to find its settings in task06/ folder):
uv run syndicate test    

* Logs can be found in task06/.syndicate-config-dev/logs folder

# 14. Build the artifacts of the application and create a bundle:
uv run syndicate build   
  
* In case of build errors of failed tests you will get an error message.


# 15. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose  
  
* In case of errors see a log in ./task06/.syndicate-condif-dev/ directory


# 16. Verify that lambda function exists:
aws lambda list-functions \
    --query 'Functions[].FunctionName' \
    --output table

* cmtr-mxhmo8sx-audit_producer

# 17. Verify that both tables of DynamoDB exists:
aws dynamodb list-tables

* cmtr-mxhmo8sx-Audit
* cmtr-mxhmo8sx-Configuration

# 18. Check the content of cmtr-mxhmo8sx-Audit:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Audit

# 19. Check the content of cmtr-mxhmo8sx-Configuration:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Configuration

# 20. Check that cmtr-mxhmo8sx-Configuration stream is enabled:
aws dynamodb describe-table --table-name cmtr-mxhmo8sx-Configuration

* Look for the following content:
"StreamSpecification": {
  "StreamEnabled": true,
  "StreamViewType": "NEW_AND_OLD_IMAGES"
}


# 21. Check that Event Source Mapping was created:
aws lambda list-event-source-mappings --function-name cmtr-mxhmo8sx-audit_producer:learn


# 22. Perform an end-to-end test. Insert a record:
aws dynamodb put-item \
  --table-name cmtr-mxhmo8sx-Configuration \
  --item '{
    "key":{"S":"CACHE_TTL_SEC"},
    "value":{"N":"3600"}
  }'

# 23. Check the content of cmtr-mxhmo8sx-Audit. It must have a record:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Audit

# 24. IN CASE OF ERROR get error messages from CLoudFront:
aws logs tail /aws/lambda/cmtr-mxhmo8sx-audit_producer --follow

# 25. Commit and push.
