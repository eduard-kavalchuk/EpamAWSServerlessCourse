REGION="eu-west-1"

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

aws apigateway get-resources \
  --rest-api-id ${API_ID}

