# 1. Sync dependencies from pyproject.toml
uv sync

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Create a syndicated project
uv run syndicate generate project --name task07

# 4. Switch to task07/ directory:
cd task07/

# 5. Generate a config that Syndicate will use to access AWS account where project will be deployed:
uv run syndicate generate config --name "dev" \
    --region "eu-west-1" \
    --deploy-target-bucket "syndicate-education-platform-custom-sandbox-artifacts-3136/mxhmo8sx/task07" \
    --prefix "cmtr-mxhmo8sx-" \
    --extended-prefix "true" \
    --tags "run_id:JAP-35,task_id:task07,topic_id:stm,user_id:mxhmo8sx" \
    --access-key "ASIAZ7SAKYLVJTY3K4BX" \
    --secret-key "2eKMNwFA1ccAUl+szZTzdNaDURe3BXLJjNmQkBAK" \
    --session-token "IQoJb3JpZ2luX2VjEBMaDGV1LWNlbnRyYWwtMSJIMEYCIQDR+3PpolUeb/EsFLElBIyDal72p9bxcMCWWVsJVEGLywIhAKnoMqNRQmcY3o4/IpEC9azGUewpwJSVej7L70v5gfn6KtECCNz//////////wEQABoMNjg2MjU1OTQ4NTIyIgxtcPqQIvei6pA56XUqpQKD06LGk4t6DcZ/xGFC07BMoo9XrGo1YCU/eCWQ5WZMfWBPqaPkTu4QVlukAsM7Q8UnNuXV67F3KMlZ9tCPBRg3h8iVmkT9OH99DIipMvZl2c2YL6V424h+LU1Ti4V0ojqYlt6SQXIuowJa6jUVB4ANs4sdYcKy3TquYIO5FynwRmj/egn3u0YB0vnP3MwkF1W/J6L+wYEX8SldIe6q0WV9Y9l25EwhioSz2uuQl2mEeAuiDMVZ5oM6ab6st/8jPBFd2o/FlFi/ywPfRwLWT+GSmWlVPuq8AvCZBvwawaM5rj5pe7wIW8MxxEeqiL+sN5NkgBlGFrGE94/t/Zyj0E48nd+ckXhubPmq3l5uRmbW7ABoE+2XWSx/Ol85QXSBKISHo5xmhjDjmeXUBjqcATu7/GiRjBPiy5xRg3U2cIy4FbTUfTdVxxMTkadsO1clPXisIiZsWAnDUTAlLK9nGJxsJL2cpOhK2Mqfe2LFMPV5Rs4C+kCqgYVba+m06rgSU5UaH4We7cp1+U7ylzM+JSf/Avfc/2ElgTpxJBkXXB7F71jXJ74au//CvjSWMrShfww1e33PgIyfsMxd0T+NnZeB6nCQvyNbUGAifA=="

# 6. Generate a config that Syndicate will use to access AWS account where project will be deployed:
export SDCT_CONF="/home/ed/EpamAWSServerlessCourse/task07/.syndicate-config-dev"

# 7. Generate metadata for the DynamoDB table named "Events":
uv run syndicate generate meta dynamodb \
    --resource-name Events \
    --hash-key-name key \
    --hash-key-type S

# 8. Generate IAM role metadata to be used with the AppSync:
uv run uv run syndicate generate meta iam-role \
  --resource-name AppSyncRole \
  --principal-service appsync.amazonaws.com

# 9. Replace AppSyncRole resource in deployment_resources.json:
"AppSyncRole": {
    "resource_type": "iam_role",
    "iam_role_name": "AppSyncRole",
    "dependencies": [
      "AppSyncDynamoPolicy"
    ],
    "assume_role_policy": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "appsync.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }
  }


# 10. Generate IAM policy to be used by AppSync:
uv run syndicate generate meta iam-policy \
  --resource-name AppSyncDynamoPolicy


# 11. Replace AppSyncDynamoPolicy resource in deployment_resources.json:
"AppSyncDynamoPolicy": {
    "resource_type": "iam_policy",
    "policy_name": "AppSyncDynamoPolicy",
    "policy_content": {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:GetItem",
            "dynamodb:PutItem"
          ],
          "Resource": "*"
        }
      ]
    }
 }

# 12. Create API:
uv run syndicate generate appsync api \
  --name GraphQL_API

# 13. Add the DynamoDB datasource:
uv run syndicate generate appsync data-source \
    --api-name GraphQL_API \
    --name EventsDataSource \
    --type AMAZON_DYNAMODB \
    --resource-name Events \
    --service-role-name AppSyncRole

# 14. Create the createEvent Resolver:
uv run syndicate generate appsync resolver \
  --api-name GraphQL_API \
  --kind UNIT \
  --type-name Mutation \
  --field-name createEvent \
  --data-source-name EventsDataSource \
  --runtime JS

# 15. Create the getEvent Resolver:
uv run syndicate generate appsync resolver \
  --api-name GraphQL_API \
  --kind UNIT \
  --type-name Query \
  --field-name getEvent \
  --data-source-name EventsDataSource \
  --runtime JS

# 16. Replace appsync_src/GraphQL_API/schema.graphql:
scalar AWSJSON
scalar AWSDateTime

type Meta {
  key1: Int!
  key2: String!
}

type Payload {
  meta: Meta!
}

type Event {
  id: ID!
  userId: Int!
  createdAt: AWSDateTime!
  payLoad: Payload!
}

type CreateEventResponse {
  id: ID!
  createdAt: AWSDateTime!
}

type Query {
  getEvent(id: ID!): Event
}

type Mutation {
  createEvent(
    userId: Int!
    payLoad: AWSJSON!
  ): CreateEventResponse!
}

# 17. Build the artifacts of the application and create a bundle:
uv run syndicate build  

# 18. Deploy the bundle (takes up to a minute for this task):
uv run syndicate deploy --verbose 

# 19. Verify that both tables of DynamoDB exists:
aws dynamodb list-tables

* cmtr-mxhmo8sx-Events

# 20. Check the content of cmtr-mxhmo8sx-Events:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Events

# 21. Find your role name:
aws iam list-roles \
  --query "Roles[?contains(RoleName, 'AppSync')].RoleName"

* cmtr-mxhmo8sx-AppSyncRole

# 22. Inspect policies attached to cmtr-mxhmo8sx-AppSyncRole:
aws iam list-attached-role-policies \
  --role-name cmtr-mxhmo8sx-AppSyncRole
  
* It must include "cmtr-mxhmo8sx-AppSyncDynamoPolicy"

# 23. See inline policies of cmtr-mxhmo8sx-AppSyncRole:
aws iam list-role-policies \
  --role-name cmtr-mxhmo8sx-AppSyncRole


# 24. See the trust policy of cmtr-mxhmo8sx-AppSyncRole:
aws iam get-role \
  --role-name cmtr-mxhmo8sx-AppSyncRole

# 25. Confirm that the AppSync API exists:
aws appsync list-graphql-apis

* ApiID: 7ja52cnvhrbu3cs7xiw52nu5xi

# 26. Get API details:
aws appsync get-graphql-api \
  --api-id 7ja52cnvhrbu3cs7xiw52nu5xi

* You should see:
    API name: GraphQL_API
    Authentication: API_KEY

# 27. Verify datasource:
aws appsync list-data-sources \
  --api-id 7ja52cnvhrbu3cs7xiw52nu5xi

* You should see
"name": "EventsDataSource",
"type": "AMAZON_DYNAMODB",

# 28. Verify the first resolver:
aws appsync get-resolver \
  --api-id 7ja52cnvhrbu3cs7xiw52nu5xi \
  --type-name Mutation \
  --field-name createEvent

# 29. Verify the second resolver:
aws appsync get-resolver \
  --api-id 7ja52cnvhrbu3cs7xiw52nu5xi \
  --type-name Query \
  --field-name getEvent

# From now on we are starting to actually send an get events to AppSync.

# 30. Get the GraphQL endpoint:
aws appsync get-graphql-api \
  --api-id 7ja52cnvhrbu3cs7xiw52nu5xi

* Look for:
"uris": {
    "REALTIME": "wss://viaechaovnbrjkoyv7oe4n7olq.appsync-realtime-api.eu-west-1.amazonaws.com/graphql",
    "GRAPHQL": "https://viaechaovnbrjkoyv7oe4n7olq.appsync-api.eu-west-1.amazonaws.com/graphql"
},

* So the API is:
https://viaechaovnbrjkoyv7oe4n7olq.appsync-api.eu-west-1.amazonaws.com/graphql

# 31. Get the API key:
aws appsync list-api-keys --api-id 7ja52cnvhrbu3cs7xiw52nu5xi

* Look for 
{
  "id": "da2-5sqjxqsxq5evloy5ot6xjltkg4"
}

* So ID is:
da2-5sqjxqsxq5evloy5ot6xjltkg4

# 32. Execute createEvent:
curl -X POST \
  "https://viaechaovnbrjkoyv7oe4n7olq.appsync-api.eu-west-1.amazonaws.com/graphql" \
  -H "Content-Type: application/json" \
  -H "x-api-key: da2-5sqjxqsxq5evloy5ot6xjltkg4" \
  -d '{
    "query":"mutation createEvent($userId:Int!, $payLoad:AWSJSON!) { createEvent(userId:$userId, payLoad:$payLoad) { id createdAt } }",
    "variables":{
      "userId":123,
      "payLoad":"{\"meta\":{\"key1\":1,\"key2\":\"test_value\"}}"
    }
  }'

* Response should look like follows:
{
    "data": {
        "createEvent": {
            "id":"d72735af-76f8-4339-84ba-ab77573f5c40",
            "createdAt":"2026-09-03T12:27:02.291Z"
        }
    }
}

* Even ID that was created is (use it in getEvent command later):
d72735af-76f8-4339-84ba-ab77573f5c40



# 32. Make sure DB contains event that was created:
aws dynamodb scan --table-name cmtr-mxhmo8sx-Events

* Make sure DB contains one item


# 33. Execute getEvent:
curl -X POST \
  "https://viaechaovnbrjkoyv7oe4n7olq.appsync-api.eu-west-1.amazonaws.com/graphql" \
  -H "Content-Type: application/json" \
  -H "x-api-key: da2-5sqjxqsxq5evloy5ot6xjltkg4" \
  -d '{
    "query":"query getEvent($id:ID!) { getEvent(id:$id) { id userId createdAt payLoad { meta { key1 key2 } } } }",
    "variables":{
      "id":"d72735af-76f8-4339-84ba-ab77573f5c40"
    }
  }'

* Event stored previously must be returned

# 34. Commit and push.

For Syndicate, generated metadata is the source of truth. When in doubt, generate a temporary resource and inspect the generated schema instead of relying on generic AWS examples.
