#!/bin/bash

# Variables
IAM_ROLE="cmtr-mxhmo8sx-iam-sewk-iam_role"
BUCKET_1="cmtr-mxhmo8sx-iam-sewk-bucket-5180421-1"
BUCKET_2="cmtr-mxhmo8sx-iam-sewk-bucket-5180421-2"
KMS_KEY_ARN="arn:aws:kms:eu-west-1:913524907044:key/b238672f-6f7d-43e5-9ca9-7c8a6dab7743"

echo "🔵 Step 1: Granting KMS permissions to the role..."

# Create KMS policy
cat > kms-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:GenerateDataKey",
                "kms:Decrypt",
                "kms:Encrypt",
                "kms:ReEncrypt*",
                "kms:DescribeKey"
            ],
            "Resource": "${KMS_KEY_ARN}"
        }
    ]
}
EOF

# Attach KMS policy to the role
aws iam put-role-policy \
    --role-name ${IAM_ROLE} \
    --policy-name AllowKMSKeyUsage \
    --policy-document file://kms-policy.json

if [ $? -eq 0 ]; then
    echo "✅ KMS permissions granted to role"
else
    echo "❌ Failed to grant KMS permissions to role!"
    echo "Exiting..."
    exit 1
fi

echo "🔵 Step 2: Enabling default encryption on bucket-2..."

# Create encryption configuration
cat > encryption-config.json << EOF
{
    "Rules": [
        {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "${KMS_KEY_ARN}"
            },
            "BucketKeyEnabled": false
        }
    ]
}
EOF

# Apply encryption configuration
aws s3api put-bucket-encryption \
    --bucket ${BUCKET_2} \
    --server-side-encryption-configuration file://encryption-config.json

if [ $? -eq 0 ]; then
    echo "✅ Default encryption enabled on bucket-2"
else
    echo "❌ Failed to enable default encryption on bucket-2!"
    echo "Exiting..."
    exit 1
fi

echo "🔵 Step 3: Enforcing encryption with bucket policy..."

# Create bucket policy to enforce encryption
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${BUCKET_2}/*",
            "Condition": {
                "Null": {
                    "s3:x-amz-server-side-encryption": "true"
                }
            }
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${BUCKET_2}/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "aws:kms"
                }
            }
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${BUCKET_2}/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption-aws-kms-key-id": "${KMS_KEY_ARN}"
                }
            }
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket ${BUCKET_2} \
    --policy file://bucket-policy.json

if [ $? -eq 0 ]; then
    echo "✅ Encryption enforcement policy applied"
else
    echo "❌ Failed to apply encryption enforcement policy!"
    echo "Exiting..."
    exit 1
fi

# Cleanup
rm -f kms-policy.json encryption-config.json bucket-policy.json
