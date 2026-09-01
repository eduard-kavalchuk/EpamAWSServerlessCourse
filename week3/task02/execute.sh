#!/bin/bash

# Set variables
BUCKET_NAME="cmtr-mxhmo8sx-s3-snlt-bucket-184475"
QUEUE_NAME="cmtr-mxhmo8sx-s3-snlt-queue"
LAMBDA_FUNCTION="cmtr-mxhmo8sx-s3-snlt-lambda"
REGION="eu-west-1"

# Get the SQS queue URL and ARN
QUEUE_URL=$(aws sqs get-queue-url --queue-name "${QUEUE_NAME}" --region "${REGION}" --output text)
QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url "${QUEUE_URL}" --attribute-names QueueArn --region "${REGION}" --output text --query 'Attributes.QueueArn')

echo "Queue URL: ${QUEUE_URL}"
echo "Queue ARN: ${QUEUE_ARN}"

# Step 1: Create S3 event notification for input/ prefix
echo "Creating S3 event notification..."
aws s3api put-bucket-notification-configuration \
    --bucket "${BUCKET_NAME}" \
    --notification-configuration '{
        "QueueConfigurations": [
            {
                "QueueArn": "'"${QUEUE_ARN}"'",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {
                                "Name": "prefix",
                                "Value": "input/"
                            }
                        ]
                    }
                }
            }
        ]
    }' \
    --region "${REGION}"

if [ ${?} -eq 0 ]; then
    echo "✅ S3 event notification created successfully"
else
    echo "❌ Failed to create S3 event notification"
    exit 1
fi

# Step 2: Configure Lambda trigger in SQS
echo "Creating Lambda event source mapping for SQS..."
aws lambda create-event-source-mapping \
    --function-name "${LAMBDA_FUNCTION}" \
    --event-source-arn "${QUEUE_ARN}" \
    --region "${REGION}" \
    --enabled

if [ ${?} -eq 0 ]; then
    echo "✅ Lambda trigger configured successfully"
else
    echo "❌ Failed to configure Lambda trigger"
    exit 1
fi

# Step 3: Wait for the trigger to be created (optional)
echo "Waiting for trigger to be fully created..."
sleep 5

# Verify the event source mapping
echo "Verifying event source mapping..."
aws lambda list-event-source-mappings \
    --function-name "${LAMBDA_FUNCTION}" \
    --region "${REGION}" \
    --query 'EventSourceMappings[?EventSourceArn==`'"${QUEUE_ARN}"'`].[UUID,State]' \
    --output table

echo "✅ Setup complete!"