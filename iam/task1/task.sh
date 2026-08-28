#!/bin/bash

# Variables
POLICY_FILE_NAME="policy.json"
ROLE="cmtr-mxhmo8sx-iam-peld-iam_role"
BUCKET="cmtr-mxhmo8sx-iam-peld-bucket-3073266"

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')

# Create and attach an inline identity-based policy to ${ROLE} role that allows all buckets to be listed
echo "🔵 Step 1: Granting full access to the Amazon S3 service for the ${ROLE} role..."

aws iam attach-role-policy \
    --role-name ${ROLE} \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

if [ $? -eq 0 ]; then
    echo "✅ Full access granted"
else
    echo "❌ Failed to grant full access!"
    echo "Exiting..."
    exit 1
fi

echo "🔵 Step 2: Update the resource-based S3 bucket policy to prohibit the deletion of any objects inside the ${BUCKET} bucket specifically for the ${ROLE} role"

cat > ${POLICY_FILE_NAME} << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE}"
            },
            "Action": [
                "s3:DeleteObject",
                "s3:DeleteObjectVersion"
            ],
            "Resource": "arn:aws:s3:::${BUCKET}/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${BUCKET} \
    --policy file://${POLICY_FILE_NAME}

if [ $? -eq 0 ]; then
    echo "✅ Policy updated"
else
    echo "❌ Failed to update policy!"
    echo "Exiting..."
    exit 1
fi


# Cleanup
rm -f ${POLICY_FILE_NAME}

echo "✅ All tasks completed successfully!"

echo "✅ Run ./test.sh for verification"
