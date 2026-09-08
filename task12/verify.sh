REGION="eu-west-1"


echo "🔵 Checking if lambda function api_handler exists..."

LAMBDA_FUNCTION_NAME=$(aws lambda list-functions \
    --query 'Functions[?contains(FunctionName, `api_handler`)].FunctionName' \
    --output text 2>/dev/null)

if [ -z "$LAMBDA_FUNCTION_NAME" ]; then
    echo "❌ No function found with 'api_handler' in the name"
    exit 1
else
    echo "✅ ${LAMBDA_FUNCTION_NAME}"
fi


echo "🔵 Checking if API gateway exists..."

API_GATEWAY_ID=$(aws apigateway get-rest-apis \
    --query 'items[*].[id]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_ID" ]; then
    echo "❌ No API gateway found"
    exit 1
else
    echo "✅ ${API_GATEWAY_ID}"
fi

API_GATEWAY_NAME=$(aws apigateway get-rest-apis \
    --query 'items[*].[name]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_NAME" ]; then
    echo "❌ No API gateway found"
    exit 1
else
    echo "✅ ${API_GATEWAY_NAME}"
fi


echo "🔵 Checking if DB tables exist..."

TABLE_RESERVATIONS=$(aws dynamodb list-tables \
    --query 'TableNames[?contains(@, `Reservations`)]' \
    --output text 2>/dev/null)

if [ -z "$TABLE_RESERVATIONS" ]; then
    echo "❌ Reservations table does not exist"
    exit 1
else
    echo "✅ ${TABLE_RESERVATIONS}"
fi

TABLE_TABLES=$(aws dynamodb list-tables \
    --query 'TableNames[?contains(@, `Reservations`)]' \
    --output text 2>/dev/null)

if [ -z "$TABLE_TABLES" ]; then
    echo "❌ Tables table does not exist"
    exit 1
else
    echo "✅ ${TABLE_TABLES}"
fi


# echo "🔵 Checking POST /signup..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signup)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking POST /signin..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signin)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi

# echo "🔵 Checking POST /tables..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /tables..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking POST /reservation..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservation)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /reservation..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservation)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /tables/{tableId} with a random tableId..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables/123)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


echo "🔵 Getting Cognito UserPool name and ID..."

COGNITO_USERPOOL_NAME=$(aws cognito-idp list-user-pools --max-results 1 --query 'UserPools[0].Name' --output text 2>/dev/null)

if [ -z "$COGNITO_USERPOOL_NAME" ] || [ "$COGNITO_USERPOOL_NAME" = "None" ]; then
    echo "❌ Error: No user pool found or unable to retrieve name"
    exit 1
else
    echo "✅ ${COGNITO_USERPOOL_NAME}"
fi

COGNITO_USERPOOL_ID=$(aws cognito-idp list-user-pools --max-results 1 --query 'UserPools[0].Id' --output text 2>/dev/null)
echo "✅ ${COGNITO_USERPOOL_ID}"


echo "🔵 Trying to signup by sending POST request to /signup endpoint..."

curl -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "John",
        "lastName": "Smith",
        "email": "john@example.com",
        "password": "Password123$"
      }'


echo "🔵 Getting Cognito list of users..."

COGNITO_USERS_LIST=$(aws cognito-idp list-users --user-pool-id "$COGNITO_USERPOOL_ID")

if [ "$(echo "$COGNITO_USERS_LIST" | jq '.Users | length')" -gt 0 ]; then
    echo "✅ Users array is not empty. Found users."
    echo "$COGNITO_USERS_LIST" | jq '.Users'
else
    echo "❌ Users array is empty. No users found."
    exit 1
fi


# echo "🔵 Checking POST /signup..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signup)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking POST /signin..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signin)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi

# echo "🔵 Checking POST /tables..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /tables..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking POST /reservation..."
# RESPONSE=$(curl -s -X POST https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservation)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /reservation..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservation)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi


# echo "🔵 Checking GET /tables/{tableId} with a random tableId..."
# RESPONSE=$(curl -s https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables/123)

# echo "Response: $RESPONSE"

# STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

# if [ "$STATUS_CODE" -ne 200 ]; then
#     echo "❌ Error: Expected statusCode 200, but got $STATUS_CODE"
#     exit 1
# else
#     echo "✅ Success: statusCode is 200"
# fi

