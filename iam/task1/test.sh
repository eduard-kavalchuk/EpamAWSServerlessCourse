#!/bin/bash

# Bash script to verify that all permissions were configured correctly
TEST_FILE="test-file.txt"
ROLE="cmtr-mxhmo8sx-iam-peld-iam_role"
BUCKET_NAME="cmtr-mxhmo8sx-iam-peld-bucket-3073266"

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE}"

# Step 0: Save your default AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN:
CREDS=$(aws configure export-credentials)
DEFAULT_AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.AccessKeyId')
DEFAULT_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.SecretAccessKey')
DEFAULT_SESSION_TOKEN=$(echo $CREDS | jq -r '.SessionToken')

# Step 1-2: Create and upload test file
echo "🔵 Creating test file..."
echo "test content" > ${TEST_FILE}
aws s3 cp ${TEST_FILE} s3://${BUCKET_NAME}/
if [ $? -eq 0 ]; then
    echo "✅ Test file uploaded"
else
    echo "❌ Failed to upload test file!"
    echo "Exiting..."
    exit 1
fi

# Step 3: Test as current identity
echo "🔵 Testing delete as current identity..."
aws s3 rm s3://${BUCKET_NAME}/${TEST_FILE}
if [ $? -eq 0 ]; then
    echo "✅ Delete succeeded (as expected for non-role identity)"
else
    echo "❌ Failed to delete test file!"
fi

# Step 4: Re-upload
echo "🔵 Re-uploading test file..."
aws s3 cp ${TEST_FILE} s3://${BUCKET_NAME}/

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
aws s3 rm s3://${BUCKET_NAME}/${TEST_FILE}

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

# Setp 10. Delete tmp files
rm ${TEST_FILE}
