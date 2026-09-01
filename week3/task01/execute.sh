#!/bin/bash

# Variables
aws_region="eu-west-1"
lambda_function="cmtr-mxhmo8sx-iam-lp-lambda"
iam_role="cmtr-mxhmo8sx-iam-lp-iam_role"
apigatewayv2_api="cmtr-mxhmo8sx-iam-lp-apigwv2_api"
account_id=$(aws sts get-caller-identity --query Account --output text)
api_id=$(aws apigatewayv2 get-apis --query "Items[?Name=='${apigatewayv2_api}'].ApiId" --output text)

echo "🔵 Step 1: Granting permissions to ${iam_role}..."

# Create KMS policy
cat > list-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:ListTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
EOF

# Attach policy to the role
aws iam put-role-policy \
    --role-name ${iam_role} \
    --policy-name LambdaListFunctionsPolicy \
    --policy-document file://list-policy.json

if [ $? -eq 0 ]; then
    echo "✅ List permissions granted to ${iam_role}"
else
    echo "❌ Failed to grant list permissions to ${iam_role}!"
    echo "Exiting..."
    exit 1
fi


echo "🔵 Step 2: Granting API Gateway Permission to ${apigatewayv2_api} API Gateway..."

aws lambda add-permission \
  --function-name ${lambda_function} \
  --statement-id apigateway-invoke-http \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${aws_region}:${account_id}:${api_id}/*/*/*"

# Check if permission was added
if [ $? -eq 0 ]; then
    echo "✅ Permission granted successfully!"
else
    echo "❌ Failed to grant permission"
    echo "Exiting..."
    exit 1
fi


echo "🔵 Step 3: [Testing] Fetching a list of Lambda functions"

# Fetch endpoint with error handling
if endpoint=$(aws apigatewayv2 get-api \
    --api-id ${api_id} \
    --query 'ApiEndpoint' \
    --output text 2>/dev/null); then
    echo "✅ Endpoint: ${endpoint}"
else
    echo "❌ Failed to fetch endpoint. Check your API ID and permissions."
    exit 1
fi

# To get a correct endpoint that returns a list of lambda functions do the following:
# 1. $endpoint is a base URL. If you go to it it returns {"message": "Not found"}.
# 2. So to get the resourse path do the following:
# a) aws apigatewayv2 get-stages --api-id ${api_id} and look for "StageName".
# If it is $default then no stage have to be specified in URL path
# b) aws apigatewayv2 get-routes --api-id 4cr1bz8f9f and look for "RouteKey"
# It will contain "GET /get_list". So /get_list is the correct URL.

curl -X GET ${endpoint}/get_list



# Cleanup
rm -f list-policy.json
