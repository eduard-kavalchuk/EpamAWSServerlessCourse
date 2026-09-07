# ------- [ Testing the deploy ] --------------------------------------

# 1. Verify that lambda function exists:
aws lambda list-functions \
    --query 'Functions[].FunctionName' \
    --output table

* cmtr-mxhmo8sx-processor

# 2. Verify that Weather table of DynamoDB exists:
aws dynamodb list-tables

* cmtr-mxhmo8sx-Weather

# 3. Check the content of cmtr-mxhmo8sx-Weather:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Weather

* There should be no items

# 4. Verify Function URL:
aws lambda get-function-url-config \
    --function-name cmtr-mxhmo8sx-processor:learn

* "FunctionUrl": "https://6fnjajpuovkpklu72bpwvyaf4u0pdxhf.lambda-url.eu-west-1.on.aws/"

# 5. Test the function:
curl https://6fnjajpuovkpklu72bpwvyaf4u0pdxhf.lambda-url.eu-west-1.on.aws/

# 6. Check the content of cmtr-mxhmo8sx-Weather:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Weather

# ----------- [ Verify X-Ray ] ----------------------------

# 1. Make sure "TracingConfig" is "Active":
aws lambda get-function-configuration \
  --function-name cmtr-mxhmo8sx-processor:learn

* Look for:
"TracingConfig": {
    "Mode": "Active"
}

# 2. Query X-Ray:
aws xray get-service-graph \
  --start-time $(date -u -d "15 minutes ago" +%s) \
  --end-time $(date -u +%s)

* JSON must be not empty
