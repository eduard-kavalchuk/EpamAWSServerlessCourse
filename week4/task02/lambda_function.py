from datetime import datetime, timezone
import boto3

cloudtrail = boto3.client("cloudtrail")


def lambda_handler(event, context):
    start_time = datetime.fromtimestamp(
        int(event["start_time"]),
        tz=timezone.utc
    )

    end_time = datetime.fromtimestamp(
        int(event["end_time"]),
        tz=timezone.utc
    )

    users = set()
    next_token = None

    while True:
        kwargs = {
            "StartTime": start_time,
            "EndTime": end_time
        }

        if next_token:
            kwargs["NextToken"] = next_token

        response = cloudtrail.lookup_events(**kwargs)

        users.update(
            e["Username"]
            for e in response.get("Events", [])
            if "Username" in e
        )

        next_token = response.get("NextToken")

        if not next_token:
            break

    return sorted(users)