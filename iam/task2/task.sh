#!/bin/bash

# Variables
ROLE="cmtr-mxhmo8sx-iam-pela-iam_role"
BUCKET="cmtr-mxhmo8sx-iam-pela-bucket-1-4118380"

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')

# Create and attach an inline identity-based policy to ${ROLE} role that allows all buckets to be listed
echo "🔵 Step 1: Create and attach an inline identity-based policy to ${ROLE} role that allows all buckets to be listed"

cat > identity_policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::${BUCKET}",
                "arn:aws:s3:::${BUCKET}/*"
            ]
        }
    ]
}
EOF

# Attach the policy to the assume role
echo "Attaching the policy to the assume role"

aws iam put-role-policy \
    --role-name ${ROLE} \
    --policy-name AllowListAllBucketsAndBucket1Operations \
    --policy-document file://identity_policy.json

if [ $? -eq 0 ]; then
    echo "✅ Inline identity-based policy attached"
else
    echo "❌ Failed to attach identity-based policy!"
    echo "Exiting..."
    exit 1
fi

echo "🔵 Step 2: Creating a resource-based S3 bucket policy..."

cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE}"
            },
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::${BUCKET}",
                "arn:aws:s3:::${BUCKET}/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${BUCKET} \
    --policy file://bucket-policy.json

if [ $? -eq 0 ]; then
    echo "✅ Resource-based S3 bucket policy is created"
else
    echo "❌ Failed to create resource-based S3 bucket policy!"
    echo "Exiting..."
    exit 1
fi

# Cleanup
rm -f assume-role-policy.json trust-policy.json

echo "✅ All tasks completed successfully!"

echo "✅ Run ./test.sh for verification"
