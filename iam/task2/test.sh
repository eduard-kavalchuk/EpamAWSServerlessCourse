#!/bin/bash

TMP_FILE="test.txt"
DOWNLOADED_FILE="download.txt"

echo "Test file" > ${TMP_FILE}

BUCKET="cmtr-mxhmo8sx-iam-pela-bucket-1-4118380"
BUCKET2="cmtr-mxhmo8sx-iam-pela-bucket-2-4118380"
ROLE="cmtr-mxhmo8sx-iam-pela-iam_role"

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE}"

# Step 0: Save your current AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN (four your current role):
CREDS=$(aws configure export-credentials)
DEFAULT_AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.AccessKeyId')
DEFAULT_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.SecretAccessKey')
DEFAULT_SESSION_TOKEN=$(echo $CREDS | jq -r '.SessionToken')

CREDS=$(aws sts assume-role --role-arn ${ROLE_ARN} --role-session-name "DeleteTestSession")

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

# This should work - list all buckets
aws s3 ls
if [ $? -eq 0 ]; then
    echo "✅ Listing all buckets succeeded"
fi

# This should work - list objects in bucket-1
aws s3 ls s3://${BUCKET}/
if [ $? -eq 0 ]; then
    echo "✅ Listing objects in bucket-1 succeeded"
fi

# This should work - upload to bucket-1
aws s3 cp ${TMP_FILE} s3://${BUCKET}/
if [ $? -eq 0 ]; then
    echo "✅ Uploade succeeded!"
else
    echo "❌ Upload DENIED! The bucket policy is not working!"
fi

# This should work - download from bucket-1
aws s3 cp s3://${BUCKET}/${TMP_FILE} ${DOWNLOADED_FILE}
if [ $? -eq 0 ]; then
    echo "✅ Download succeeded!"
else
    echo "❌ Download DENIED! The bucket policy is not working!"
fi

# These should FAIL - access to bucket-2
aws s3 ls s3://${BUCKET2}/
if [ $? -eq 0 ]; then
    echo "❌ Listing bucket-2 ALLOWED! The bucket policy is not working!"
else
    echo "✅ Listing bucket-2 DENIED! The bucket policy is working!"
fi

aws s3 cp ${TMP_FILE} s3://${BUCKET2}/
if [ $? -eq 0 ]; then
    echo "❌ Copying to bucket-2 ALLOWED! The bucket policy is not working!"
else
    echo "✅ Copying to bucket-2 DENIED! The bucket policy is working!"
fi

# Step 9: Cleanup: Unset credentials (you can skip it because default credentials are set  in the next step)
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN

# Step 10: Set default credentials
export AWS_ACCESS_KEY_ID=$(echo $DEFAULT_AWS_ACCESS_KEY_ID)
export AWS_SECRET_ACCESS_KEY=$(echo $DEFAULT_SECRET_ACCESS_KEY)
export AWS_SESSION_TOKEN=$(echo $DEFAULT_SESSION_TOKEN)

# Step 11. Delete temp files
rm ${TMP_FILE} ${DOWNLOADED_FILE}