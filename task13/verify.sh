REGION="eu-west-1"
FIRST_NAME="John"
LAST_NAME="Smith"
EMAIL="john@example.com"
PASSWORD="Password1234$"
TABLE_ID=1

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
    --query 'TableNames[?contains(@, `Tables`)]' \
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

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signup \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "'"${FIRST_NAME}"'",
        "lastName": "'"${LAST_NAME}"'",
        "email": "'"${EMAIL}"'",
        "password": "'"${PASSWORD}"'"
      }')

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

echo ${RESPONSE}

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

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/signin \
  -H "Content-Type: application/json" \
  -d '{
        "email": "'"${EMAIL}"'",
        "password": "'"${PASSWORD}"'"
      }')

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

echo ${RESPONSE}

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed get signin tokens. Status: $STATUS_CODE"
    exit 1
fi

ID_TOKEN=$(echo "$RESPONSE" | jq -r '.idToken')

echo
echo ID_TOKEN=${ID_TOKEN}


echo
echo "🔵 Creating a table..."

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables \
  -H "Content-Type: application/json" \
  -d '{
        "id": '"${TABLE_ID}"',
        "number": 7,
        "places": 4,
        "isVip": false,
        "minOrder": 100
      }')


STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

echo ${RESPONSE}

CREATED_TABLE_ID=$(echo "$RESPONSE" | jq -r '.id')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed to create table"
    exit 1
fi


echo
echo "🔵 Fetching all tables..."

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables)

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed to fetch tables"
    exit 1
fi

echo "$RESPONSE" | jq -r '.tables'


echo
echo "🔵 Creating a reservation..."

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservations \
  -H "Content-Type: application/json" \
  -d '{
        "tableNumber": '"${TABLE_ID}"',
        "clientName": "John Smith",
        "phoneNumber": "+375291112233",
        "date": "2026-09-10",
        "slotTimeStart": "13:00",
        "slotTimeEnd": "15:00"
      }')

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed to fetch reservations"
    exit 1
fi


echo
echo "🔵 Fetching all reservations..."

RESPONSE=$(curl -s -w "\n%{http_code}" https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/reservations)

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed to fetch reservations"
    exit 1
fi

echo "$RESPONSE" | jq -r '.body | fromjson | .reservations'


echo
echo "🔵 Fetching table data for table with ID=${CREATED_TABLE_ID}..."

RESPONSE=$(curl -s -w "\n%{http_code}" https://${API_GATEWAY_ID}.execute-api.${REGION}.amazonaws.com/api/tables/${CREATED_TABLE_ID})

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success"
else
    echo "❌ Failed to fetch table data"
    exit 1
fi

echo "$RESPONSE"
