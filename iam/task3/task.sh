#!/bin/bash

# Variables
ASSUME_ROLE="cmtr-mxhmo8sx-iam-ar-iam_role-assume"
READONLY_ROLE="cmtr-mxhmo8sx-iam-ar-iam_role-readonly"

CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')

echo "🔵 Step 1: Creating identity-based policy for assume role..."

# Create policy that allows assuming the readonly role
echo "Creating policy that allows assuming the readonly role..."

cat > assume-role-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::${ACCOUNT_ID}:role/${READONLY_ROLE}"
        }
    ]
}
EOF

# Attach the policy to the assume role
echo "Attaching the policy to the assume role"

aws iam put-role-policy \
    --role-name ${ASSUME_ROLE} \
    --policy-name AllowAssumeReadonlyRole \
    --policy-document file://assume-role-policy.json

if [ $? -eq 0 ]; then
    echo "✅ Assume role policy attached"
else
    echo "❌ Failed to attach assume policy!"
fi

echo "🔵 Step 2: Attaching ReadOnlyAccess to readonly role..."

# Attach AWS managed ReadOnlyAccess policy
echo "Attaching AWS managed ReadOnlyAccess policy..."

aws iam attach-role-policy \
    --role-name ${READONLY_ROLE} \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

if [ $? -eq 0 ]; then
    echo "✅ ReadOnlyAccess attached to readonly role"
else
    echo "❌ Failed to attach ReadOnlyAccess"
fi

echo "🔵 Step 3: Configuring trust policy on readonly role..."

# Create trust policy
echo "Creating trust policy..."

cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:role/${ASSUME_ROLE}"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Update the readonly role's trust policy
echo "Updating the readonly role's trust policy..."

aws iam update-assume-role-policy \
    --role-name ${READONLY_ROLE} \
    --policy-document file://trust-policy.json

if [ $? -eq 0 ]; then
    echo "✅  Trust policy configured on readonly role"
else
    echo "❌ Failed to configured trust policy on readonly role"
fi

# Cleanup
rm -f assume-role-policy.json trust-policy.json

echo "✅ All tasks completed successfully!"

echo "✅ Run ./test.sh for verification"
