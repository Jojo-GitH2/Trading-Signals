import json
import boto3
import datetime
import time


def lambda_handler(event, context):
    # Parse input parameters from event
    h = int(event["h"])
    d = int(event["d"])
    t = event["t"]
    p = int(event["p"])
    s = event["s"]
    r = event["r"]
    instance_id = event["instance_id"]
    table_name = event["table_name"]

    # Initialize SDK

    ssm = boto3.client("ssm")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    command = f"cd /home/ec2-user && python3 risk_analysis.py {h} {d} {t} {p}"

    # Send commands to ec2 instance

    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={
            "commands": [command],
        },
    )

    command_id = response["Command"]["CommandId"]

    table.put_item(
        Item={
            "CommandId": command_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "s": s,
            "r": r,
            "h": h,
            "d": d,
            "t": t,
            "p": p,
        }
    )

    while True:
        response = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
        )
        if response["Status"] != "InProgress":
            break
        time.sleep(1)

    # # results = json.loads(response['StandardOutputContent'])

    # output_content = response.get('StandardOutputContent')
    # if output_content:
    #     results = json.loads(output_content)
    # else:
    #     results = {}

    # table.update_item(
    #     Key={'CommandId': command_id},
    #     UpdateExpression='SET results = :results',
    #     ExpressionAttributeValues={':results': results},
    # )

    return {"statusCode": 200, "body": json.dumps({"command_id": command_id})}


# Test Event
# {
#     "h": "101",
#     "d": "10000",
#     "t": "sell",
#     "p": "7",
#     "s": "ec2",
#     "r": 1,
#     "table_name": "trading-signals-results",
#     "instance_id": "i-0eeb3eec242dc444b",
# }
