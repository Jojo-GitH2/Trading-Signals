import json
import boto3


def lambda_handler(event, context):

    service = event["service"]
    scale = event["scale"]

    # Create a session using your user's credentials
    session = boto3.session.Session()

    if service.lower() == "ec2":
        ec2_client = session.client("ec2")
        response = ec2_client.run_instances(
            ImageId="ami-0c101f26f147fa7fd",
            InstanceType="t2.micro",
            MaxCount=int(scale),
            MinCount=int(scale),
        )

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
