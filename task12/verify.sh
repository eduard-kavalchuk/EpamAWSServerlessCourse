REGION="eu-west-1"
FIRST_NAME="John"
LAST_NAME="Smith"
EMAIL="john@example.com"
PASSWORD="Password123$"

echo
echo "🔵 Checking if lambda function api_handler exists..."

LAMBDA_FUNCTION_NAME=$(aws lambda list-functions \
    --query 'Functions[?contains(FunctionName, `api_handler`)].FunctionName' \
    --output text 2>/dev/null)

if [ -z "$LAMBDA_FUNCTION_NAME" ]; then
    echo "❌ No function found with 'api_handler' in the name"
    exit 1
else
    echo "✅ LAMBDA_FUNCTION_NAME=${LAMBDA_FUNCTION_NAME}"
fi

echo
echo "🔵 Checking if API gateway exists..."

API_GATEWAY_ID=$(aws apigateway get-rest-apis \
    --query 'items[*].[id]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_ID" ]; then
    echo "❌ No API gateway found"
    exit 1
else
    echo "✅ API_GATEWAY_ID=${API_GATEWAY_ID}"
fi

API_GATEWAY_NAME=$(aws apigateway get-rest-apis \
    --query 'items[*].[name]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_NAME" ]; then
    echo "❌ No API gateway found"
    exit 1
else
    echo "✅ API_GATEWAY_NAME=${API_GATEWAY_NAME}"
fi

echo
echo https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api

echo
echo "🔵 Checking if DB tables exist..."

TABLE_RESERVATIONS=$(aws dynamodb list-tables \
    --query 'TableNames[?contains(@, `Reservations`)]' \
    --output text 2>/dev/null)

if [ -z "$TABLE_RESERVATIONS" ]; then
    echo "❌ Reservations table does not exist"
    exit 1
else
    echo "✅ TABLE_RESERVATIONS=${TABLE_RESERVATIONS}"
fi

TABLE_TABLES=$(aws dynamodb list-tables \
    --query 'TableNames[?contains(@, `Reservations`)]' \
    --output text 2>/dev/null)

if [ -z "$TABLE_TABLES" ]; then
    echo "❌ Tables table does not exist"
    exit 1
else
    echo "✅ TABLE_TABLES=${TABLE_TABLES}"
fi

echo
echo "🔵 Getting Cognito UserPool name and ID..."

COGNITO_USERPOOL_NAME=$(aws cognito-idp list-user-pools --max-results 1 --query 'UserPools[0].Name' --output text 2>/dev/null)

if [ -z "$COGNITO_USERPOOL_NAME" ] || [ "$COGNITO_USERPOOL_NAME" = "None" ]; then
    echo "❌ Error: No user pool found or unable to retrieve name"
    exit 1
else
    echo "✅ COGNITO_USERPOOL_NAME=${COGNITO_USERPOOL_NAME}"
fi

COGNITO_USERPOOL_ID=$(aws cognito-idp list-user-pools --max-results 1 --query 'UserPools[0].Id' --output text 2>/dev/null)
echo "✅ COGNITO_USERPOOL_ID=${COGNITO_USERPOOL_ID}"

echo
echo "🔵 Trying to signup by sending POST request to /signup endpoint..."

RESPONSE=$(curl -s -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "'"${FIRST_NAME}"'",
        "lastName": "'"${LAST_NAME}"'",
        "email": "'"${EMAIL}"'",
        "password": "'"${PASSWORD}"'"
      }')

echo ${RESPONSE}
STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed with status: $STATUS_CODE"
    exit 1
fi

echo
echo "🔵 Getting Cognito list of users..."

COGNITO_USERS_LIST=$(aws cognito-idp list-users --user-pool-id "$COGNITO_USERPOOL_ID")

if [ "$(echo "$COGNITO_USERS_LIST" | jq '.Users | length')" -gt 0 ]; then
    echo "✅ Users array is not empty. Found users:"
    echo "$COGNITO_USERS_LIST" | jq '.Users'
else
    echo "❌ Users array is empty. No users found."
    exit 1
fi

echo
echo "🔵 Getting access tokens (POST /signin)..."

RESPONSE=$(curl -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signin \
  -H "Content-Type: application/json" \
  -d '{
        "email": "'"${EMAIL}"'",
        "password": "'"${PASSWORD}"'"
      }')

STATUS_CODE=$(echo "$RESPONSE" | jq -r '.statusCode')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed get signin tokens. Status: $STATUS_CODE"
    exit 1
fi

ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.body | fromjson | .accessToken')
REFRESH_TOKEN=$(echo "$RESPONSE" | jq -r '.body | fromjson | .refreshToken')
ID_TOKEN=$(echo "$RESPONSE" | jq -r '.body | fromjson | .idToken')

echo
echo ACCESS_TOKEN=${ACCESS_TOKEN}
echo
echo REFRESH_TOKEN=${REFRESH_TOKEN}
echo
echo ID_TOKEN=${ID_TOKEN}



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

