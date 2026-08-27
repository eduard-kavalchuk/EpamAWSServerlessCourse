#!/bin/bash

BUCKET_NAME="cmtr-mxhmo8sx-iam-pela-bucket-1-3753451"
ROLE_ARN="arn:aws:iam::536697226993:role/cmtr-mxhmo8sx-iam-pela-iam_role"

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
aws s3 ls s3://cmtr-mxhmo8sx-iam-pela-bucket-1-3753451/
if [ $? -eq 0 ]; then
    echo "✅ Listing objects in bucket-1 succeeded"
fi

# This should work - upload to bucket-1
aws s3 cp test.txt s3://cmtr-mxhmo8sx-iam-pela-bucket-1-3753451/
if [ $? -eq 0 ]; then
    echo "✅ Uploade succeeded!"
else
    echo "❌ Upload DENIED! The bucket policy is not working!"
fi

# This should work - download from bucket-1
aws s3 cp s3://cmtr-mxhmo8sx-iam-pela-bucket-1-3753451/test.txt downloaded.txt
if [ $? -eq 0 ]; then
    echo "✅ Download succeeded!"
else
    echo "❌ Download DENIED! The bucket policy is not working!"
fi

# These should FAIL - access to bucket-2
aws s3 ls s3://cmtr-mxhmo8sx-iam-pela-bucket-2-3753451/
if [ $? -eq 0 ]; then
    echo "❌ Listing bucket-2 ALLOWED! The bucket policy is not working!"
else
    echo "✅ Listing bucket-2 DENIED! The bucket policy is working!"
fi

aws s3 cp test.txt s3://cmtr-mxhmo8sx-iam-pela-bucket-2-3753451/
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
