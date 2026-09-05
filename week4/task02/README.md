# 1. Get the name of your lambda function:
aws lambda list-functions --query "Functions[*].[FunctionName,Runtime,MemorySize,LastModified]" --output table

* cmtr-mxhmo8sx-lambda-fgufc-lambda

# 2. Prepare payload.json file to send request to lambda function:
echo '{"start_time":"2026-09-01T00:00:00Z","end_time":"2026-09-05T23:59:59Z"}' > payload.json

* With echo command there is no chance to get unexpected extra characters 

# 3. Invoke lambda function to make sure it works:
aws lambda invoke \
  --function-name cmtr-mxhmo8sx-lambda-fgufc-lambda \
  --cli-binary-format raw-in-base64-out \
  --payload file://payload.json \
  response.json

* It is important to have the following option specified:
--cli-binary-format raw-in-base64-out
Without this option CLI will append extra UTF characters to the outgoing message and you will get unexpected and hard-to-understand errors.

# 4. Write a new lambda function. Make sure the function is stored in a file whose name is exactly the same as the one on AWS.

# 5. Zip the file containing function:
zip lambda_function.zip lambda_function.py

# 6. Deploy the function:
aws lambda update-function-code \
  --function-name cmtr-mxhmo8sx-lambda-fgufc-lambda \
  --zip-file fileb://lambda_function.zip

# 7. Verify your deployment either via Management Console by just looking at function's code or using the following command:
aws lambda get-function \
  --function-name cmtr-mxhmo8sx-lambda-fgufc-lambda \
  --query 'Configuration.[FunctionName,LastModified,CodeSize]'

# 8. Create a test payload:
echo '{"start_time":"2026-09-05T20:00:00Z","end_time":"2026-09-05T23:59:59Z"}' > payload.json

# 9. Invoke the function:
aws lambda invoke \
  --function-name cmtr-mxhmo8sx-lambda-fgufc-lambda \
  --cli-binary-format raw-in-base64-out \
  --payload file://payload.json \
  response.json

# --- [ Viewing logs ] -------------------------------------------------------
The easiest way to see logs is to:
1. Open Management Console
2. Go to your lambda function
3. Click the Monitor tab
4. Click View CloudWatch logs
