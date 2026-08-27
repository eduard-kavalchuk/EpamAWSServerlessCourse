#!/bin/bash

# Bash script to verify that all permissions were configured correctly

BUCKET_NAME="cmtr-mxhmo8sx-iam-peld-bucket-7269810"
ROLE_ARN="arn:aws:iam::692859931137:role/cmtr-mxhmo8sx-iam-peld-iam_role"

# Step 0: Save your default AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN:
CREDS=$(aws configure export-credentials)
DEFAULT_AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.AccessKeyId')
DEFAULT_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.SecretAccessKey')
DEFAULT_SESSION_TOKEN=$(echo $CREDS | jq -r '.SessionToken')

# Step 1-2: Create and upload test file
echo "🔵 Creating test file..."
echo "test content" > test-file.txt
aws s3 cp test-file.txt s3://${BUCKET_NAME}/
echo "✅ Test file uploaded"

# Step 3: Test as current identity
echo "🔵 Testing delete as current identity..."
aws s3 rm s3://${BUCKET_NAME}/test-file.txt
if [ $? -eq 0 ]; then
    echo "✅ Delete succeeded (as expected for non-role identity)"
fi

# Step 4: Re-upload
echo "🔵 Re-uploading test file..."
aws s3 cp test-file.txt s3://${BUCKET_NAME}/

# Step 5: Assume the role
echo "🔵 Assuming the role..."
CREDS=$(aws sts assume-role --role-arn ${ROLE_ARN} --role-session-name "DeleteTestSession")

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

# Step 7: Confirm identity
echo "🔵 Current identity:"
aws sts get-caller-identity

# Step 8: Attempt to delete as the role
echo "🔵 Attempting delete as the role..."
aws s3 rm s3://${BUCKET_NAME}/test-file.txt

if [ $? -eq 0 ]; then
    echo "❌ Delete succeeded! Deny isn't working."
else
    echo "✅ Delete DENIED! The bucket policy is working."
fi

# Step 9: Cleanup: Unset credentials (you can skip it because default credantials are set  in the next step)
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

# Step 10: Set default credantials
export AWS_ACCESS_KEY_ID=$(echo $DEFAULT_AWS_ACCESS_KEY_ID)
export AWS_SECRET_ACCESS_KEY=$(echo $DEFAULT_SECRET_ACCESS_KEY)
export AWS_SESSION_TOKEN=$(echo $DEFAULT_SESSION_TOKEN)
