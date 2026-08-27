echo "Test 1: Can the Assume Role Assume the Readonly Role?"
echo

# Step 0: Save your current AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN (four your current role):
echo "Saving current credentials..."

CREDS=$(aws configure export-credentials)
DEFAULT_AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.AccessKeyId')
DEFAULT_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.SecretAccessKey')
DEFAULT_SESSION_TOKEN=$(echo $CREDS | jq -r '.SessionToken')

# Get account ID
echo "Getting Account ID..."

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')

# Assume cmtr-mxhmo8sx-iam-ar-iam_role-assume role
echo "Trying to assume cmtr-mxhmo8sx-iam-ar-iam_role-assume role..."

CREDS=$(aws sts assume-role --role-arn arn:aws:iam::${ACCOUNT_ID}:role/cmtr-mxhmo8sx-iam-ar-iam_role-assume --role-session-name "TestSession")

if [ $? -eq 0 ]; then
    echo "✅ cmtr-mxhmo8sx-iam-ar-iam_role-assume role was assumed!"
else
    echo "❌ cmtr-mxhmo8sx-iam-ar-iam_role-assume role was not assumed!"
fi

# Export the credentials
echo "Exporting new credentials..."

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')


# Now try to assume the readonly role
echo "Trying to assume cmtr-mxhmo8sx-iam-ar-iam_role-readonly role..."

CREDS=$(aws sts assume-role --role-arn arn:aws:iam::${ACCOUNT_ID}:role/cmtr-mxhmo8sx-iam-ar-iam_role-readonly --role-session-name "TestReadonlySession")

if [ $? -eq 0 ]; then
    echo "✅ Readonly role was assumed!"
else
    echo "❌ Readonly role was not assumed!"
fi

# Export the credentials
export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')


# Other tests

echo
echo "Test 2: Read-Only Access Works"
echo

aws iam list-users
if [ $? -eq 0 ]; then
    echo "✅ All users listed. Policy is working!"
else
    echo "❌ Failed to list users. Policy is not working!"
fi

echo
echo "Test 3: Write Access Fails"
echo

aws iam create-user --user-name test-user
if [ $? -eq 0 ]; then
    echo "❌ Creating a user was ALLOWED. Policy is not working!"
else
    echo "✅ Creating a user was DENIED. Policy is working!"
fi

# Cleanup
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
export AWS_ACCESS_KEY_ID=$(echo $DEFAULT_AWS_ACCESS_KEY_ID)
export AWS_SECRET_ACCESS_KEY=$(echo $DEFAULT_SECRET_ACCESS_KEY)
export AWS_SESSION_TOKEN=$(echo $DEFAULT_SESSION_TOKEN)