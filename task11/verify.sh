REGION="eu-west-1"
student_access_sg_id="sg-0583d8ff9f131702c"
DB_NAME="logisticdb"


echo
echo "🔵 Checking if lambda function api_handler exists..."

FUNCTION_API_HANDLER=$(aws lambda list-functions \
    --query 'Functions[?contains(FunctionName, `api_handler`)].FunctionName' \
    --output text 2>/dev/null)

if [ -z "$FUNCTION_API_HANDLER" ]; then
    echo "❌ No function found with 'api_handler' in the name"
else
    echo "✅ FUNCTION_API_HANDLER=${FUNCTION_API_HANDLER}"
fi


echo
echo "🔵 Checking if lambda function batch_processor exists..."

FUNCTION_BATCH_PROCESSOR=$(aws lambda list-functions \
    --query 'Functions[?contains(FunctionName, `batch_processor`)].FunctionName' \
    --output text 2>/dev/null)

if [ -z "$FUNCTION_BATCH_PROCESSOR" ]; then
    echo "❌ No function found with 'batch_processor' in the name"
else
    echo "✅ FUNCTION_BATCH_PROCESSOR=${FUNCTION_BATCH_PROCESSOR}"
fi

echo
echo "🔵 Checking if API gateway exists..."

API_GATEWAY_ID=$(aws apigateway get-rest-apis \
    --query 'items[?contains(name, `logistic_API`)].[id]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_ID" ]; then
    echo "❌ No API gateway found"
else
    echo "✅ API_GATEWAY_ID=${API_GATEWAY_ID}"
fi

API_GATEWAY_NAME=$(aws apigateway get-rest-apis \
    --query 'items[?contains(name, `logistic_API`)].[name]' \
    --output text 2>/dev/null)

if [ -z "$API_GATEWAY_NAME" ]; then
    echo "❌ No API gateway found"
else
    echo "✅ API_GATEWAY_NAME=${API_GATEWAY_NAME}"
fi


echo
echo "🔵 Checking status of the cluster..."

CLUSTER_NAME=$(aws rds describe-db-clusters \
  --query "DBClusters[?contains(DBClusterIdentifier, 'logistic-cluster')].[DBClusterIdentifier]" --output text 2>/dev/null)

if [ -z "$CLUSTER_NAME" ]; then
    echo "❌ No API gateway found"
else
    echo "✅ CLUSTER_NAME=${CLUSTER_NAME}"
fi

CLUSTER_AVAILABILITY=$(aws rds describe-db-clusters \
--query "DBClusters[?contains(DBClusterIdentifier, 'logistic-cluster')].[Status]" --output text 2>/dev/null)

if [ "$CLUSTER_AVAILABILITY" = "available" ]; then
    echo "✅ Status of the cluster: ${CLUSTER_AVAILABILITY}"
else
    echo "❌ Status of the cluster: ${CLUSTER_AVAILABILITY}"
fi


echo
echo "🔵 Checking status of RDS instance..."

RDS_INSTANCE_NAME=$(aws rds describe-db-instances \
  --query "DBInstances[?contains(DBInstanceIdentifier, 'logistic-instance')].[DBInstanceIdentifier]" --output text 2>/dev/null)

if [ -z "$RDS_INSTANCE_NAME" ]; then
    echo "❌ No RDS instance found"
else
    echo "✅ RDS_INSTANCE_NAME=${RDS_INSTANCE_NAME}"
fi

RDS_INSTANCE_AVAILABILITY=$(aws rds describe-db-instances \
--query "DBInstances[?contains(DBInstanceIdentifier, 'logistic-instance')].[DBInstanceStatus]" --output text 2>/dev/null)

if [ "$RDS_INSTANCE_AVAILABILITY" = "available" ]; then
    echo "✅ Status of the instance: ${RDS_INSTANCE_AVAILABILITY}"
else
    echo "❌ Status of the instance: ${RDS_INSTANCE_AVAILABILITY}"
fi


echo
echo "🔵 Checking availability of S3 bucket..."

BUCKET_ARN=$(aws s3api head-bucket \
  --bucket cmtr-mxhmo8sx-data-transfer-storage  --query "BucketArn" --output text 2>/dev/null)

if [ -z "$BUCKET_ARN" ]; then
    echo "❌ No bucket found"
else
    echo "✅ BUCKET_ARN=${RDS_INSTANCE_AVAILABILITY}"
fi


echo
echo "🔵 Checking if S3 trigger is attached..."

aws s3api get-bucket-notification-configuration \
  --bucket cmtr-mxhmo8sx-data-transfer-storage


echo
echo "🔵 Checking VPC configuration of api_handler function..."

aws lambda get-function-configuration \
--function-name cmtr-mxhmo8sx-api_handler \
--query "VpcConfig"


echo
echo "🔵 Checking VPC configuration of batch_processor function..."

aws lambda get-function-configuration \
  --function-name cmtr-mxhmo8sx-batch_processor \
  --query "VpcConfig"


echo
echo "🔵 Checking that Aurora cluster endpoint exists..."

aws rds describe-db-clusters \
  --db-cluster-identifier cmtr-mxhmo8sx-logistic-cluster \
  --query "DBClusters[0].[Endpoint,ReaderEndpoint]"


echo
echo "🔵 Checking that Aurora cluster password is managed by Secrets Manager..."

aws rds describe-db-clusters \
  --db-cluster-identifier cmtr-mxhmo8sx-logistic-cluster \
  --query "DBClusters[0].MasterUserSecret"


echo
echo "🔵 Verifying API structure..."

API_ID=$(aws apigateway get-rest-apis \
  --query "items[?starts_with(name,'cmtr-mxhmo8sx-logistic_API')].id" \
  --output text)

echo "✅ API_ID=${API_ID}"

echo
BASE_URL=https://${API_ID}.execute-api.${REGION}.amazonaws.com/api
echo "✅ BASE_URL=$BASE_URL)"


echo
echo "🔵 Invoke endpoint: initdb"

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://${API_ID}.execute-api.${REGION}.amazonaws.com/api/initdb)

STATUS_CODE=$(echo "$HTTP_RESPONSE" | tail -n1)
RESPONSE=$(echo "$HTTP_RESPONSE" | sed '$d')

if [ "$STATUS_CODE" -eq 200 ]; then
    echo "✅ Success (status code $STATUS_CODE)"
else
    echo "❌ Failed to initialize database (status code $STATUS_CODE)"
fi

echo "✅ Received response: $RESPONSE"


echo

AURORA_CLUSTER=$(aws lambda get-function-configuration \
  --function-name $FUNCTION_API_HANDLER \
  --query "Environment.Variables.DB_SECRET_NAME" \
  --output text)

echo AURORA_CLUSTER=$AURORA_CLUSTER

SECRET=$(aws secretsmanager get-secret-value \
  --secret-id $AURORA_CLUSTER \
  --query SecretString \
  --output text)

USERNAME=$(echo "$SECRET" | jq -r '.username')
PASSWORD=$(echo "$SECRET" | jq -r '.password')

echo
echo "USERNAME=$USERNAME"
echo "PASSWORD=$PASSWORD"

RDS_CLUSTER_ENDPOINT=$(aws rds describe-db-clusters \
  --db-cluster-identifier $CLUSTER_NAME \
  --query "DBClusters[0].Endpoint" \
  --output text \
  --region eu-west-1)

echo
echo "RDS_CLUSTER_ENDPOINT=$RDS_CLUSTER_ENDPOINT"


echo
echo "🔵 Getting my IP..."
IP=$(curl -s curl ifconfig.me)
echo "My IP=$IP"

aws ec2 authorize-security-group-ingress \
  --group-id $student_access_sg_id \
  --protocol tcp \
  --port 5432 \
  --cidr $IP/32 \
  --region $REGION

echo
echo "🔵 Trying to connect to database..."
nc -vz $RDS_CLUSTER_ENDPOINT 5432

echo
echo "🔵 List of tables:"
PGPASSWORD=$PASSWORD psql \
  -h $RDS_CLUSTER_ENDPOINT \
  -U $USERNAME \
  -d $DB_NAME \
  -c "\dt"


echo
echo "🔵 Create shipment..."
curl -X POST "$BASE_URL/shipments" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id":"ship001",
    "order_id":"order001",
    "origin":"Minsk",
    "destination":"Warsaw",
    "weight_kg":10.5
  }'
  

echo
echo "🔵 Get shipment..."
curl "$BASE_URL/shipments/ship001"

echo
echo "🔵 Update shipment..."
curl -X PATCH "$BASE_URL/shipments/ship001" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id":"order001_updated",
    "origin":"Vilnius",
    "destination":"Berlin",
    "weight_kg":15.0
  }'

echo
echo "🔵 Vefiry shipment update..."
curl "$BASE_URL/shipments/ship001"

echo
echo "🔵 Create carrier..."
curl -X POST "$BASE_URL/carriers" \
  -H "Content-Type: application/json" \
  -d '{
    "carrier_id":"car001",
    "name":"DHL",
    "email":"dhl@test.com",
    "phone":"+1234567",
    "is_active":true
  }'

echo
echo "🔵 Get carrier..."
curl "$BASE_URL/carriers/car001"

echo
echo "🔵 Update carrier..."
curl -X PATCH "$BASE_URL/carriers/car001" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"DHL Express",
    "email":"express@test.com",
    "phone":"+7654321",
    "is_active":true
  }'

echo
echo "🔵 Verify carrier update..."
curl "$BASE_URL/carriers/car001"

echo
echo "🔵 Create status update..."
curl -X POST "$BASE_URL/statusupdates" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id":"ship001",
    "carrier_id":"car001",
    "status":"CREATED",
    "location":"Minsk",
    "notes":"initial status"
  }'

echo
echo "🔵 Read status updates..."
curl "$BASE_URL/statusupdates/ship001"

echo
echo "🔵 Delete carrier..."
curl -X DELETE "$BASE_URL/carriers/car001"

echo
echo "🔵 Delete shipment..."
curl -X DELETE "$BASE_URL/shipments/ship001"

echo
echo "🔵 Verify deletions..."
curl "$BASE_URL/shipments/ship001"

echo
echo "🔵 Invalid shipment..."
curl "$BASE_URL/shipments/does_not_exist"

echo
echo "🔵 Invalid carrier..."
curl "$BASE_URL/carriers/does_not_exist"

echo
echo "🔵 Invalid status..."
curl -X POST "$BASE_URL/statusupdates" \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_id":"ship001",
    "carrier_id":"car001",
    "status":"BAD_STATUS",
    "location":"Minsk",
    "notes":"x"
  }'



