# 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Copy task12/:
cp -r task12/ task13/

# 4. Delete settings of task13/:
rm -fr .syndicate-config-dev/

# 5. Generate a project:
uv run syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-2516/mxhmo8sx/task13" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task13,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAXTORPMOM45Z5NOIY" \
    --secret-key "4rTo9a4EF8hxNf9su7EMWa8NdshUKy575fJklges" \
    --session-token "IQoJb3JpZ2luX2VjEM///////////wEaDGV1LWNlbnRyYWwtMSJIMEYCIQCRRKWXvyH2kuON7Otqoacsj/qyfZCRlPNT9xUKoupTHgIhAO1osd8VJ9+E8D4FlC3YHvKQvl8CnU4ocfIlObQuH++zKtECCJj//////////wEQABoMNTIyODE0NzEwNjgxIgzVg5C+K+4g8ojVG2gqpQJZMiStOm4M73lFoMjLWljq/P2IjERfOoUNi7/UHPK5QD2uuP1j7PoPmuW8zZJmtmd3Jif1Dzp+AnTyc/gHFuTZDcotu11lCFbEToqYSMfohCQdlKdhHtVRcc0Ewq4hmq0kzmlWMhaXOt6IT82WIXrvdHzHwSfRv5qv3KwJFMKXLjR6nCTwo+1+dGcaSnopuSZiQPkg7jiSnGbq6TTqvTmzb2sPTQsAjizZnI+0dmdofw4d+2ZNefj+F2OSLQwyFc9NGJupxp/KhUhLoMB4qZbby1lP0a1+lC1bVmQmc1EmtsXhARf/QzSEJNilk4qWl+3a1VVF97FgQPDoinV7++zrLNpIYWz+yCFWWbNDXYByHzIcvLzMv6hxbMPSupy2HTpq3QYe2TDO0Y7VBjqcAUagMY4XGo6nVy8Mmptc1Jo9z+uOvMkdv2l5o3dPQaJoFyPywMQnsbdnNmyBZ2WB+Rgse9g8w0eayvHDdszbIB6tff3zXmc3JX+5Kk3GBASmNJE89jjmjRvUSQpQd7e3tGVjyY5c1tlzxJPGQAPR4VnwYbQI3IEYChrseGBFvcRO6SX9s4i7+/9zg0J0wgWO2w7n0tD7aI3eUGk8OQ=="

# 6. Export:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task13/.syndicate-config-dev"

# 7. Build and deploy:
uv run syndicate build
uv run syndicate deploy --verbose

# 8. Test:
./verify

NOTE!! If this script fails at geteway step then abort the whole task and re-start it!

# 9. In deployment_resources.json:
Replace "enable_cors": state false
to 
"enable_cors": state true

# 10. Modify lambda and tests to accommodate new headers.

NOTE!! Make sure in all tests replace 2026 to 2027. Otherwise, some of the tests will fail because of logical errors.

# 11. Build ,deploy, verify

Note. At the time of writing this I had no problems at this step.


# 12. DO NOT CLEAN DEPLOYMENT! GO TO STEP 13 ABOVE!

# 13. Export to OAS v3:
uv run syndicate export --resource-type api_gateway --dsl oas_v3

NOTE! A new export/ folder will appear in the root of the task13/
NOTE! You may leave you deployment running.

# 14. Go to deployment_resources.json and remove the entire "task13_api" (this is description of API gateway).

# 15. Update export/...json file as needed.

# 16. make sure you checked that the filw is correct with Co-pilot.

# 17. Build:
uv run syndicate build

# 18. Update ONLY task13_api resource:
uv run syndicate update -resources task13_api

# 19. Generate meta for S3 bucket:
uv run syndicate generate meta s3-bucket  --resource-name api-ui-hoster

# 20. Replace api_hoster with this (here 195.56.119.209/32 is my REAL IP, not IP under VPN, and it works!):
"api-ui-hoster": {
      "resource_type": "s3_bucket",
      "acl": "private",
      "cors": [],
      "policy": {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "AllowSwaggerUIAccess",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
              "s3:GetObject"
            ],
            "Resource": [
              "arn:aws:s3:::api-ui-hoster/*"
            ],
            "Condition": {
              "IpAddress": {
                "aws:SourceIp": [
                  "18.184.51.32/32",
                  "3.123.112.118/32",
                  "18.197.177.98/32",
                  "18.184.51.32/32",
                  "3.123.112.118/32",
                  "54.93.50.115/32",
                  "3.120.73.239/32",
                  "3.126.49.248/32",
                  "195.56.119.209/32"
                ]
              }
            }
          }
        ]
      },
    "public_access_block": {
      "block_public_acls": true,
      "ignore_public_acls": true,
      "block_public_policy": false,
      "restrict_public_buckets": false
    },
    "website_hosting": {
      "enabled": true,
      "index_document": "index.html",
      "error_document": "index.html"
    },
    "tags": {}
  }

# 20. Add Swagger UI Resource to Deployment Resources:
uv run syndicate generate swagger-ui --name=task13_api_ui --path-to-spec=export/0afzo2eqql_oas_v3.json --target-bucket=api-ui-hoster

# 21. Clean existing deploy:
uv run syndicate clean

# 22. Build:
uv run syndicate build

# 23. Deploy:
uv run syndicate deploy

# 24. Check if the following link works:
http://cmtr-mxhmo8sx-api-ui-hoster.s3-website-eu-west-1.amazonaws.com/index.html

* If it works it will open a page.

# 25. Verify with the script:
./verify

# 26. Clean:
uv run syndicate clean

# 27. Submit for verification.

# 28. If verificatin fails at Swagger UI step go to Syndi bot and request valid IPs.
I had this problem and it turned out that IP listed in documentation are not as they should be.
At the time of writing, correct IP are the following:
"aws:SourceIp": 
[
  "18.184.51.32/32",
  "3.123.112.118/32",
  "18.197.177.98/32",
  "18.184.51.32/32",
  "3.123.112.118/32",
  "54.93.50.115/32",
  "3.120.73.239/32",
  "3.126.49.248/32",
  "195.56.119.209/32"
]
