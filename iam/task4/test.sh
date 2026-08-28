#!/bin/bash

BUCKET_1="cmtr-mxhmo8sx-iam-sewk-bucket-5180421-1"
BUCKET_2="cmtr-mxhmo8sx-iam-sewk-bucket-5180421-2"
KMS_KEY_ARN="arn:aws:kms:eu-west-1:913524907044:key/b238672f-6f7d-43e5-9ca9-7c8a6dab7743"

echo "🔵 Step 1: Copying the file from bucket-1 to bucket-2..."

# Copy the file with encryption
aws s3 cp s3://${BUCKET_1}/confidential_credentials.csv \
    s3://${BUCKET_2}/confidential_credentials.csv \
    --sse aws:kms \
    --sse-kms-key-id ${KMS_KEY_ARN}

if [ $? -eq 0 ]; then
    echo "✅ File confidential_credentials.csv copied successfully!"
else
    echo "❌ Failed to copy confidential_credentials.csv file!"
    echo "Exiting..."
    exit 1
fi

echo "🔵 Step 2: Verifying the copy..."

# Check if file exists in bucket-2
aws s3 ls s3://${BUCKET_2}/confidential_credentials.csv

if [ $? -eq 0 ]; then
    echo "✅ File confidential_credentials.csv found in ${BUCKET_2}"
else
    echo "❌ Failed to find confidential_credentials.csv file in ${BUCKET_2}!"
    echo "Exiting..."
    exit 1
fi

# Check encryption status (will show if encrypted)
aws s3api head-object \
    --bucket ${BUCKET_2} \
    --key confidential_credentials.csv \
    --query 'ServerSideEncryption'

if [ $? -eq 0 ]; then
    echo "✅ File confidential_credentials.csv is encrypted"
else
    echo "❌ File confidential_credentials.csv is not encrypted!"
fi


echo "🔵 Test 1: Upload with the Correct KMS Key (Should Succeed)"
echo "test" > test-correct.txt
aws s3 cp test-correct.txt s3://${BUCKET_2}/test-correct.txt \
    --sse aws:kms \
    --sse-kms-key-id ${KMS_KEY_ARN}

if [ $? -eq 0 ]; then
    echo "✅ Successfully uploaded file encrypted with a correct KMS key"
else
    echo "❌ Failed to upload file encrypted with a correct KMS key"
fi


echo "🔵 Test 2: Upload with the Wrong KMS Key (Should Fail)"
echo "test" > test-wrong.txt
aws s3 cp test-wrong.txt s3://${BUCKET_2}/test-wrong.txt \
    --sse aws:kms \
    --sse-kms-key-id "arn:aws:kms:eu-west-1:913524907044:key/wrong-key-id"

if [ $? -eq 0 ]; then
    echo "❌ Uploading was allowed"
else
    echo "✅ Uploading was denied"
fi


echo "🔵 Test 3: Upload with No Encryption (Should Fail)"
echo "test" > test-no-encrypt.txt
aws s3 cp test-no-encrypt.txt s3://${BUCKET_2}/test-no-encrypt.txt

if [ $? -eq 0 ]; then
    echo "❌ Uploading was allowed"
else
    echo "✅ Uploading was denied"
fi


echo "🔵 Test 4: Upload with AES256 (Should Fail)"
echo "test" > test-aes.txt
aws s3 cp test-aes.txt s3://${BUCKET_2}/test-aes.txt \
    --sse AES256

if [ $? -eq 0 ]; then
    echo "❌ Uploading was allowed"
else
    echo "✅ Uploading was denied"
fi


# Cleanup
rm test-*
