#!/bin/bash

# Configuration variables (these would be replaced by your actual values)
AWS_REGION="eu-west-1"
API_GATEWAY_ID="3v2e7d2b99"
ROUTE_ID="kiie9ba"
LAMBDA_FUNCTION_NAME="cmtr-mxhmo8sx-api-gwlp-lambda-contacts"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting API Gateway-Lambda integration setup...${NC}"

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Step 1: Get current Lambda configuration to determine the correct handler
echo -e "${YELLOW}Step 1: Checking Lambda function configuration...${NC}"

LAMBDA_CONFIG=$(aws lambda get-function-configuration \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$AWS_REGION" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Could not get Lambda function configuration.${NC}"
    exit 1
fi

CURRENT_HANDLER=$(echo "$LAMBDA_CONFIG" | grep -o '"Handler": "[^"]*"' | cut -d'"' -f4)
CURRENT_RUNTIME=$(echo "$LAMBDA_CONFIG" | grep -o '"Runtime": "[^"]*"' | cut -d'"' -f4)

echo -e "${GREEN}Current handler: $CURRENT_HANDLER${NC}"
echo -e "${GREEN}Current runtime: $CURRENT_RUNTIME${NC}"

# Extract the filename from the handler (everything before the first dot)
HANDLER_FILE=$(echo "$CURRENT_HANDLER" | cut -d'.' -f1)
HANDLER_FUNCTION=$(echo "$CURRENT_HANDLER" | cut -d'.' -f2)

echo -e "${GREEN}Handler file: $HANDLER_FILE.py${NC}"
echo -e "${GREEN}Handler function: $HANDLER_FUNCTION${NC}"

# Step 2: Update Lambda function code using the existing handler name
echo -e "${YELLOW}Step 2: Updating Lambda function code...${NC}"

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

# Create the Lambda function with the correct filename
cat > "${HANDLER_FILE}.py" << EOF
import json

def ${HANDLER_FUNCTION}(event, context):
    """
    Lambda function to handle API Gateway requests and return contacts list
    """
    # Handle GET /contacts request
    # Get the path from either rawPath (HTTP API) or path (REST API)
    path = event.get('rawPath', event.get('path', ''))
    http_method = event.get('httpMethod', '')
    
    # Extract the stage name from the path if present
    # The path might be /stage/contacts or /contacts
    # We need to handle both cases
    path_parts = path.strip('/').split('/')
    
    # Check if path ends with 'contacts' or 'contacts/'
    contact_path = None
    
    if path.endswith('/contacts') or path.endswith('/contacts/'):
        contact_path = '/contacts'
    elif '/contacts' in path:
        contact_path = '/contacts'
    else:
        # If no 'contacts' in path, check if it's just the stage name
        # and we need to add /contacts
        if len(path_parts) == 1 and 'stage' in path:
            contact_path = '/contacts'
    
    # If we still don't have a contact path, check if the raw path ends with contacts
    if not contact_path:
        if path == '/contacts' or path == '/contacts/':
            contact_path = '/contacts'
    
    if http_method == 'GET' and contact_path == '/contacts':
        contacts = [
            {"id": 1, "name": "Elma Herring", "email": "elmaherring@unq.com", "phone": "+1 (913) 497-2020"},
            {"id": 2, "name": "Bell Burgess", "email": "bellburgess@unq.com", "phone": "+1 (887) 478-2693"},
            {"id": 3, "name": "Hobbs Ferrell", "email": "hobbsferrell@unq.com", "phone": "+1 (862) 581-3022"}
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(contacts)
        }
    
    # Handle other requests
    return {
        'statusCode': 404,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': 'Not found',
            'path': path,
            'method': http_method,
            'message': 'Only GET /contacts is supported'
        })
    }
EOF

# Zip the Lambda code
zip -r lambda-function.zip "${HANDLER_FILE}.py"

# Update the Lambda function code
aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --zip-file fileb://lambda-function.zip \
    --region "$AWS_REGION" \
    --publish > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to update Lambda function code.${NC}"
    cd .. && rm -rf "$TEMP_DIR"
    exit 1
fi

cd .. && rm -rf "$TEMP_DIR"
echo -e "${GREEN}Lambda function code updated successfully.${NC}"

# Step 3: Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$AWS_REGION" --query 'Configuration.FunctionArn' --output text)

# Step 4: Add permission for API Gateway
echo -e "${YELLOW}Step 3: Configuring Lambda permissions...${NC}"

aws lambda remove-permission \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --statement-id "apigateway-${API_GATEWAY_ID}" \
    --region "$AWS_REGION" 2>/dev/null

aws lambda add-permission \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --statement-id "apigateway-${API_GATEWAY_ID}" \
    --action "lambda:InvokeFunction" \
    --principal "apigateway.amazonaws.com" \
    --source-arn "arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${API_GATEWAY_ID}/*" \
    --region "$AWS_REGION" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to add Lambda permission.${NC}"
    exit 1
fi
echo -e "${GREEN}Lambda permissions configured.${NC}"

# Step 5: Get existing route info and clean up old integration
echo -e "${YELLOW}Step 4: Setting up API Gateway integration...${NC}"

ROUTE_INFO=$(aws apigatewayv2 get-route \
    --api-id "$API_GATEWAY_ID" \
    --route-id "$ROUTE_ID" \
    --region "$AWS_REGION" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Route not found.${NC}"
    exit 1
fi

EXISTING_INTEGRATION=$(echo "$ROUTE_INFO" | grep -o '"IntegrationId": "[^"]*"' | cut -d'"' -f4)

if [ ! -z "$EXISTING_INTEGRATION" ] && [ "$EXISTING_INTEGRATION" != "null" ]; then
    aws apigatewayv2 delete-integration \
        --api-id "$API_GATEWAY_ID" \
        --integration-id "$EXISTING_INTEGRATION" \
        --region "$AWS_REGION" 2>/dev/null
fi

# Step 6: Create new integration
INTEGRATION_RESPONSE=$(aws apigatewayv2 create-integration \
    --api-id "$API_GATEWAY_ID" \
    --integration-type AWS_PROXY \
    --integration-method POST \
    --integration-uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations" \
    --payload-format-version 1.0 \
    --timeout-in-millis 30000 \
    --region "$AWS_REGION")

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create integration.${NC}"
    exit 1
fi

INTEGRATION_ID=$(echo "$INTEGRATION_RESPONSE" | grep -o '"IntegrationId": "[^"]*"' | cut -d'"' -f4)

if [ -z "$INTEGRATION_ID" ] || [ "$INTEGRATION_ID" == "null" ]; then
    echo -e "${RED}Error: Failed to get integration ID.${NC}"
    exit 1
fi

# Step 7: Update route with integration
aws apigatewayv2 update-route \
    --api-id "$API_GATEWAY_ID" \
    --route-id "$ROUTE_ID" \
    --route-key "GET /contacts" \
    --target "integrations/${INTEGRATION_ID}" \
    --region "$AWS_REGION" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to update route.${NC}"
    exit 1
fi
echo -e "${GREEN}Integration attached to route.${NC}"

# Step 8: Deploy the API
echo -e "${YELLOW}Step 5: Deploying the API...${NC}"

DEPLOYMENT_ID=$(aws apigatewayv2 create-deployment \
    --api-id "$API_GATEWAY_ID" \
    --region "$AWS_REGION" \
    --query 'DeploymentId' \
    --output text)

if [ -z "$DEPLOYMENT_ID" ] || [ "$DEPLOYMENT_ID" == "None" ]; then
    echo -e "${RED}Error: Failed to deploy API.${NC}"
    exit 1
fi
echo -e "${GREEN}API deployed with deployment ID: $DEPLOYMENT_ID${NC}"

# Step 9: Get API endpoint and stage
echo -e "${YELLOW}Step 6: Getting API endpoint and stage...${NC}"

API_ENDPOINT=$(aws apigatewayv2 get-api \
    --api-id "$API_GATEWAY_ID" \
    --region "$AWS_REGION" \
    --query 'ApiEndpoint' \
    --output text)

# Get the stage name
STAGE_NAME=$(aws apigatewayv2 get-stages \
    --api-id "$API_GATEWAY_ID" \
    --region "$AWS_REGION" \
    --query 'Items[0].StageName' \
    --output text)

echo -e "${GREEN}API Endpoint: ${API_ENDPOINT}${NC}"
echo -e "${GREEN}Stage Name: ${STAGE_NAME}${NC}"

# ============================================
# VERIFICATION
# ============================================
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}VERIFICATION${NC}"
echo -e "${YELLOW}========================================${NC}"

# Wait for propagation
echo -e "${YELLOW}Waiting 10 seconds for changes to propagate...${NC}"
sleep 10

# Test Lambda directly
echo -e "\n${YELLOW}Test 1: Testing Lambda function directly...${NC}"
LAMBDA_RESPONSE=$(aws lambda invoke \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --payload '{"httpMethod":"GET","path":"/contacts"}' \
    /dev/stdout \
    --region "$AWS_REGION" \
    --cli-binary-format raw-in-base64-out 2>/dev/null)

if echo "$LAMBDA_RESPONSE" | grep -q '"statusCode": 200'; then
    echo -e "${GREEN}✅ Lambda function works correctly.${NC}"
else
    echo -e "${RED}❌ Lambda function test failed.${NC}"
    echo "Response: $LAMBDA_RESPONSE"
    exit 1
fi

# Test API Gateway endpoint with stage
echo -e "\n${YELLOW}Test 2: Testing API Gateway endpoint...${NC}"

# Build the full URL with stage
if [ ! -z "$STAGE_NAME" ] && [ "$STAGE_NAME" != "None" ] && [ "$STAGE_NAME" != "null" ]; then
    TEST_URL="${API_ENDPOINT}/${STAGE_NAME}/contacts"
else
    TEST_URL="${API_ENDPOINT}/contacts"
    echo -e "${YELLOW}Warning: No stage found, testing without stage.${NC}"
fi

echo -e "${YELLOW}URL: $TEST_URL${NC}"

# Get response and status code
RESPONSE=$(curl -s -X GET "$TEST_URL" \
    -H "Content-Type: application/json" 2>/dev/null)

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$TEST_URL" \
    -H "Content-Type: application/json" 2>/dev/null)

echo -e "HTTP Status: $HTTP_CODE"

# Check if the response contains all three contacts (ignoring whitespace differences)
if [ "$HTTP_CODE" == "200" ]; then
    # Check for each contact using more flexible matching
    if echo "$RESPONSE" | grep -q '"id"[[:space:]]*:[[:space:]]*1[[:space:]]*,[[:space:]]*"name"[[:space:]]*:[[:space:]]*"Elma Herring"' && \
       echo "$RESPONSE" | grep -q '"id"[[:space:]]*:[[:space:]]*2[[:space:]]*,[[:space:]]*"name"[[:space:]]*:[[:space:]]*"Bell Burgess"' && \
       echo "$RESPONSE" | grep -q '"id"[[:space:]]*:[[:space:]]*3[[:space:]]*,[[:space:]]*"name"[[:space:]]*:[[:space:]]*"Hobbs Ferrell"'; then
        echo -e "\n${GREEN}✅✅✅ VERIFICATION SUCCESSFUL ✅✅✅${NC}"
        echo -e "${GREEN}API Gateway successfully returns the contacts list.${NC}"
        echo -e "\n${GREEN}Response:${NC}"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
        echo -e "\n${GREEN}Full working URL:${NC}"
        echo -e "${GREEN}$TEST_URL${NC}"
        exit 0
    else
        echo -e "\n${RED}❌ VERIFICATION FAILED${NC}"
        echo -e "${YELLOW}Response does not contain all expected contacts.${NC}"
        echo -e "${YELLOW}Response: $RESPONSE${NC}"
        exit 1
    fi
else
    echo -e "\n${RED}❌ VERIFICATION FAILED${NC}"
    echo -e "${YELLOW}HTTP Status: $HTTP_CODE${NC}"
    echo -e "${YELLOW}Response: $RESPONSE${NC}"
    echo -e "\n${YELLOW}Troubleshooting tips:${NC}"
    echo -e "  1. Lambda handler is: $CURRENT_HANDLER"
    echo -e "  2. File created: ${HANDLER_FILE}.py with function ${HANDLER_FUNCTION}"
    echo -e "  3. Your stage name is: $STAGE_NAME"
    echo -e "  4. Try this URL in your browser: ${API_ENDPOINT}/${STAGE_NAME}/contacts"
    echo -e "  5. Verify route key is 'GET /contacts' in AWS Console"
    echo -e "  6. Check Lambda permissions in AWS Console"
    exit 1
fi