# 1. Get the names of your lambda functions:
aws lambda list-functions --query "Functions[*].[FunctionName,Runtime,MemorySize,LastModified]" --output table

* cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct
* cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList

# 2. Update code for function cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct.

# 3. Update code for function cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList.

# ---- [ Provide permissions to function to operate DB ] ----------------------------

# 4. Find execution role for cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct:
aws lambda get-function-configuration \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --query Role \
  --output text

* arn:aws:iam::438465166519:role/cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct
* Note! Role's name in this case coincides with the name of the function: cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct


# 5. See policies attached to a role:
Note: below cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct is the ROLE name, not function's name
aws iam list-attached-role-policies \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct

"AttachedPolicies": [
    {
        "PolicyName": "AWSLambdaRole",
        "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
    }
]

# 6. See inline policies (sometimes the permissions are not attached policies but inline policies):
aws iam list-role-policies \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct

* cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct-logs

# 7. If any policy names are returned, inspect them:
aws iam get-role-policy \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --policy-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct-logs

* Look at Effects, actions and resources.

# 8. Create file dynamodb-policy.json to grant access to Dynamo DB:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/cmtr-mxhmo8sx-dynamodb-l-table-products",
        "arn:aws:dynamodb:*:*:table/cmtr-mxhmo8sx-dynamodb-l-table-stocks"
      ]
    }
  ]
}

# 9. Create the policy:
aws iam create-policy \
  --policy-name DynamoDBProductsPolicy \
  --policy-document file://dynamodb-policy.json

* "Arn": "arn:aws:iam::438465166519:policy/DynamoDBProductsPolicy"

# 10. Attach policy to Lambda role:
aws iam attach-role-policy \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --policy-arn arn:aws:iam::438465166519:policy/DynamoDBProductsPolicy

# 11. Verify the policy is attached:
aws iam list-attached-role-policies \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct


# ---- [ Repeat steps 4-11 for cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList function ] ------------------

# 12. Find execution role for cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList:
aws lambda get-function-configuration \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --query Role \
  --output text

* arn:aws:iam::438465166519:role/cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList
* Note! Role's name in this case coincides with the name of the function: cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList


# 13. See policies attached to a role:
Note: below cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct is the ROLE name, not function's name
aws iam list-attached-role-policies \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList

"AttachedPolicies": [
    {
        "PolicyName": "AWSLambdaRole",
        "PolicyArn": "arn:aws:iam::aws:policy/service-role/AWSLambdaRole"
    }
]

# 14. Attach policy to Lambda role:
aws iam attach-role-policy \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --policy-arn arn:aws:iam::438465166519:policy/DynamoDBProductsPolicy

# 15. Verify the policy is attached:
aws iam list-attached-role-policies \
  --role-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList


# ------------- [ Deploy both functions ] --------------------------------------------
# 1. Zip the file containing function:
zip create_product.zip create_product.py

# 2. Deploy the function:
aws lambda update-function-code \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --zip-file fileb://create_product.zip

# 3. Verify your deployment either via Management Console by just looking at function's code or using the following command:
aws lambda get-function \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --query 'Configuration.[FunctionName,LastModified,CodeSize]'

# 4. Zip the file containing function:
zip get_products_list.zip get_products_list.py

# 5. Deploy the function:
aws lambda update-function-code \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --zip-file fileb://get_products_list.zip

# 6. Verify your deployment either via Management Console by just looking at function's code or using the following command:
aws lambda get-function \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --query 'Configuration.[FunctionName,LastModified,CodeSize]'


# ------------ [ Gateway integration ] ------------------------------------------------------
First we need to determine whether cmtr-mxhmo8sx-dynamodb-l-api is a REST API (v1) or an HTTP API (v2). The CLI commands are different. API Gateway requires a route, integration, and Lambda invoke permissions.

# 1. Check HTTP APIs (v2):
aws apigatewayv2 get-apis

* "ApiId": "uwrl3boifd"
* In this case this is HTTP APIs gateway since response contains ApiId

# 2. Check REST APIs (v1):
aws apigateway get-rest-apis

* In this case the response is {"items": []}, which means this is not a REST gateway.
* All commands that follow below are related to HTTP APIs gateway.

# 3. Save API_ID:
API_ID=uwrl3boifd

# 4. Get Lambda ARN for createProduct:
aws lambda get-function \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --query 'Configuration.FunctionArn' \
  --output text

* arn:aws:lambda:eu-west-1:438465166519:function:cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct

# 5. Save it:
CREATE_ARN=arn:aws:lambda:eu-west-1:438465166519:function:cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct

# 6. Get Lambda ARN for getProductsList:
aws lambda get-function \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --query 'Configuration.FunctionArn' \
  --output text

* arn:aws:lambda:eu-west-1:438465166519:function:cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList

# 7. Save it:
GET_ARN=arn:aws:lambda:eu-west-1:438465166519:function:cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList

# 8. GET integration:
aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $GET_ARN \
  --payload-format-version 2.0

* "IntegrationId": "6fn7fiq"

# 9. Save it:
GET_INTEGRATION_ID=6fn7fiq

# 10. POST integration:
aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $CREATE_ARN \
  --payload-format-version 2.0

* "IntegrationId": "zxuir2u"

# 11. Save it:
POST_INTEGRATION_ID=zxuir2u

# 12. Create GET /products route:
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "GET /products" \
  --target integrations/$GET_INTEGRATION_ID

# 13. Create POST /products route:
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key "POST /products" \
  --target integrations/$POST_INTEGRATION_ID

# 14. Allow API Gateway to invoke the Lambdas. For GET Lambda:
aws lambda add-permission \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-getProductsList \
  --statement-id apigateway-get-products \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com

# 15. Allow API Gateway to invoke the Lambdas. For POST Lambda:
aws lambda add-permission \
  --function-name cmtr-mxhmo8sx-dynamodb-l-lambda-createProduct \
  --statement-id apigateway-post-products \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com

# 16. Find the invoke URL:
aws apigatewayv2 get-api \
  --api-id $API_ID

* "ApiEndpoint": "https://uwrl3boifd.execute-api.eu-west-1.amazonaws.com"


# ------------------ [ Verification ] -------------------------------------------------

1. Check POST request:
curl -X POST \
  "https://uwrl3boifd.execute-api.eu-west-1.amazonaws.com/products" \
  -H "Content-Type: application/json" \
  -H "random-uuid: test123" \
  -d '{
        "title":"Product Title",
        "description":"This product ...",
        "price":200,
        "count":2
      }'

2. Check GET request:
curl "https://uwrl3boifd.execute-api.eu-west-1.amazonaws.com/products"


If validator fails then just make fixes in an affected function and then re-deploy.


Delete all records from cmtr-mxhmo8sx-dynamodb-l-table-products:

for id in $(aws dynamodb scan \
  --table-name cmtr-mxhmo8sx-dynamodb-l-table-products \
  --query 'Items[].id.S' \
  --output text); do

  aws dynamodb delete-item \
    --table-name cmtr-mxhmo8sx-dynamodb-l-table-products \
    --key "{\"id\":{\"S\":\"$id\"}}"

done


Delete all records from cmtr-mxhmo8sx-dynamodb-l-table-stocks:

for id in $(aws dynamodb scan \
  --table-name cmtr-mxhmo8sx-dynamodb-l-table-stocks \
  --query 'Items[].product_id.S' \
  --output text); do

  aws dynamodb delete-item \
    --table-name cmtr-mxhmo8sx-dynamodb-l-table-stocks \
    --key "{\"product_id\":{\"S\":\"$id\"}}"

done

