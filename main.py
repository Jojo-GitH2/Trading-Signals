from flask import Flask, request, jsonify, render_template
import boto3
import json
import helper
import os
import time
import risk_analysis

app = Flask(__name__)

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
# Run one of this on the command line before running the code below:
# To create a secret with the AWS credentials in the Google Secret Manager
# gcloud secrets create aws-credentials  --data-file=C:\Users\Lawal\.aws\credentials --project=trading-signals-418515

# To Update the secret with the AWS credentials in the Google Secret Manager
# gcloud secrets versions add aws-credentials --data-file=C:\Users\Lawal\.aws\credentials --project=trading-signals-418515

# Authenticate with AWS
# aws_credentials = helper.get_secret(
#     project_id="trading-signals-418515", secret_id="aws-credentials"
# )

# try:
#     lines = aws_credentials.split("\n")
#     if len(lines) < 4:
#         raise ValueError("Invalid AWS credentials format")

#     aws_access_key_id = lines[1].split("=")[1].strip()
#     aws_secret_access_key = lines[2].split("=")[1].strip()
#     aws_session_token = lines[3].split("=")[1].strip()

# except IndexError:
#     print("Error: AWS credentials file is not in the expected format.")
# except ValueError as ve:
#     print(f"Error: {ve}")

# # Configure boto3 with your AWS credentials
# boto3.setup_default_session(
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     aws_session_token=aws_session_token,
# )

warmup_state = {
    "warm": False,
    "service": None,
    "terminated": True,
    "warmup_time": 0,
    "scale": 0,
    "cost": 0.0,
    "instances": [],
}

has_run = False
table_name = "trading-signals-results"


results = {}


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/", methods=["GET"])
def home():
    # This is a simple home page, also doubles as a description of the API
    return render_template("index.html")


@app.route("/warmup", methods=["POST"])
def warmup():
    try:
        global has_run
        # Get the input parameters
        data = request.get_json()
        s = data.get("service")
        r = data.get("scale")

        # Store the service in the warmup_state
        warmup_state["service"] = s
        warmup_state["scale"] = r

        # Call the Lambda function
        # lambda_client = boto3.client("lambda")
        user_data = """
#!/bin/bash
sudo yum update -y
sudo yum install -y python3 python3-pip
pip3 install yfinance boto3
echo '
import yfinance as yf
from datetime import date, timedelta
import sys
import math
import random
import json

def risk_analysis(h, d, t, p):
    # Get stock data from Yahoo Finance
    today = date.today()
    timePast = today - timedelta(days=h)
    data = yf.download("NVDA", start=timePast, end=today)
    results = {"var95": [], "var99": [], "profit_loss": []}
    # Convert the data to a list of lists
    data_list = [list(row) for row in data.values]
    count = 0
    # Perform the risk analysis for each signal
    for i in range(2, len(data_list)):
        body = 0.01
        # Three Soldiers
        if (
            (data_list[i][3] - data_list[i][0]) >= body 
            and data_list[i][3] > data_list[i - 1][3]
            and (data_list[i - 1][3] - data_list[i - 1][0]) >= body 
            and data_list[i - 1][3] > data_list[i - 2][3] 
            and (data_list[i - 2][3] - data_list[i - 2][0]) >= body
        ):
            signal = 1
        # Three Crows
        elif (
            (data_list[i][0] - data_list[i][3]) >= body
            and data_list[i][3] < data_list[i - 1][3]
            and (data_list[i - 1][0] - data_list[i - 1][3]) >= body
            and data_list[i - 1][3] < data_list[i - 2][3]
            and (data_list[i - 2][0] - data_list[i - 2][3]) >= body
        ):
            signal = -1
        else:
            signal = 0

        if (signal == 1 and t == "buy") or (signal == -1 and t == "sell"):
            # Generate d simulated returns
            mean = sum([row[3] for row in data_list[i - h : i]]) / h
            std = math.sqrt(
                sum([(row[3] - mean) ** 2 for row in data_list[i - h : i]]) / h
            )
            simulated = [random.gauss(mean, std) for _ in range(d)]
            # print(simulated)

            # Calculate the 95% and 99% VaR
            simulated.sort(reverse=True)
            var95 = simulated[int(len(simulated) * 0.95)]
            var99 = simulated[int(len(simulated) * 0.99)]
            count += 1
            results["var95"].append(var95)
            results["var99"].append(var99)

            # Calculate the profit or loss
            if i + p < len(data_list):
                if t == "buy":
                    profit_loss = data_list[i + p][3] - data_list[i][3]
                else:  # t == "sell"
                    profit_loss = data_list[i][3] - data_list[i + p][3]
                results["profit_loss"].append(profit_loss)
    # return json.dumps(results)
    with open('/home/ec2-user/data.json', 'w') as f:
        json.dump(results, f)

if __name__ == "__main__":
    h = int(sys.argv[1])
    d = int(sys.argv[2])
    t = sys.argv[3]
    p = int(sys.argv[4])
    risk_analysis(h, d, t, p)
    ' > /home/ec2-user/risk_analysis.py
"""

        # input_params = {
        #     "service": s,
        #     "scale": r,
        # }

        instances_ids = []

        start_time = time.time()
        if s.lower() == "ec2":
            # Setup resources
            # ssm = boto3.client("ssm")
            dynamodb = boto3.resource("dynamodb")
            table_name = "trading-signals-results"

            # Check if the DynamoDB table exists
            try:
                table = dynamodb.Table(table_name)
                table.table_status
            except dynamodb.meta.client.exceptions.ResourceNotFoundException:
                # If the table does not exist, create it
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {"AttributeName": "CommandId", "KeyType": "HASH"},
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "CommandId", "AttributeType": "S"},
                    ],
                    BillingMode="PAY_PER_REQUEST",
                )

            ec2_client = boto3.client("ec2")
            security_group_name = "TradingSignals"
            security_group_description = "Trading Signals Security Group"

            # Check if the security group already exists
            response = ec2_client.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [security_group_name]}]
            )
        if response["SecurityGroups"]:
            security_group_id = response["SecurityGroups"][0]["GroupId"]

        # If the security group does not exist, create it
        elif not response["SecurityGroups"]:
            response = ec2_client.create_security_group(
                GroupName=security_group_name,
                Description=security_group_description,
            )
            security_group_id = response["GroupId"]

            # Authorize inbound SSH traffic on port 22
            ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                ],
            )

        instances_running = ec2_client.describe_instances(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": ["running", "pending"],
                }
            ]
        )
        count = sum(
            len(reservation["Instances"])
            for reservation in instances_running["Reservations"]
        )

        # table.wait_until_exists()
        if count < r:
            response = ec2_client.run_instances(
                ImageId="ami-0c101f26f147fa7fd",
                InstanceType="t2.micro",
                MaxCount=int(abs(r - count)),
                MinCount=int(abs(r - count)),
                KeyName="vockey",
                UserData=user_data,
                SecurityGroupIds=[security_group_id],
            )
            instances_ids = [
                instance["InstanceId"] for instance in response["Instances"]
            ]
        elif count == r:
            instances_ids = [
                instance["InstanceId"]
                for reservation in instances_running["Reservations"]
                for instance in reservation["Instances"]
            ]
        else:
            pass
        has_run = True
        # response = lambda_client.invoke(
        #     FunctionName="warmup_services",
        #     InvocationType="RequestResponse",
        #     Payload=json.dumps(input_params),
        # )

        end_time = time.time()
        warmup_state["warmup_time"] = end_time - start_time
        # response_payload = json.load(response["Payload"])

        # if response_payload["statusCode"] == 200:
        if instances_ids != list():
            warmup_state["warm"] = True
            warmup_state["terminated"] = False
            warmup_state["instances"] = instances_ids
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify({"result": "ok"})


@app.route("/scaled_ready", methods=["GET"])
def scaled_ready():
    ec2 = boto3.resource("ec2")
    for instances in warmup_state["instances"]:
        instance = ec2.Instance(instances)
        if instance.state["Name"] != "running":
            warmup_state["warm"] = False
            break

    return jsonify({"warm": warmup_state["warm"]})


@app.route("/get_warmup_cost", methods=["GET"])
def get_warmup_cost():
    if not warmup_state["warm"]:
        return jsonify({"cost": warmup_state["cost"]})
    if warmup_state["service"] == "ec2":
        price_per_instance = 0.0116
    warmup_state["cost"] = (
        f'${price_per_instance * warmup_state["scale"] * warmup_state["warmup_time"]:.2f}'
    )
    return jsonify(
        {
            "billable_time": f'{round(warmup_state["warmup_time"], 2)} seconds',
            "cost": warmup_state["cost"],
        }
    )


@app.route("/get_endpoints", methods=["GET"])
def get_endpoints():
    ec2 = boto3.resource("ec2")
    endpoints = {}
    count = 0
    for instances in warmup_state["instances"]:
        instance = ec2.Instance(instances)
        count += 1
        endpoints[f"endpoint {count}"] = instance.public_dns_name
    return jsonify(endpoints)


@app.route("/analyse", methods=["POST"])
def analyse():
    data = request.get_json()
    h = data.get(
        "history"
    )  # the length of price history from which to generate mean and standard deviation
    d = data.get(
        "shots"
    )  # the number of data points (shots) to generate in each r for calculating risk via simulated returns
    t = data.get("buy_or_sell")
    p = data.get(
        "no_of_days"
    )  # the number of data points (shots) to generate in each r for calculating risk via simulated returns
    if warmup_state["service"].lower() == "ec2":
        # ssm = boto3.client("ssm")
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)

    # results = risk_analysis.risk_analysis(h, d, t, p)
    # # Calculate number of Shots per instance
    # shots_per_instance = d // len(warmup_state["instances"])
    # remainder = d % len(warmup_state["instances"])
    return jsonify({"result": "ok", "results": results})


@app.route("/get_sig_vars9599", methods=["GET"])
def get_sig_vars9599():
    # Retrieve the VaR values from the results
    # var95 = [result["var95"] for result in results.values()]
    # var99 = [result["var99"] for result in results.values()]
    try:
        var95 = results["var95"]
        var99 = results["var99"]
    except KeyError:
        return jsonify({"error": "No results available"})
    return jsonify({"var95": var95, "var99": var99})

    # return jsonify({"var95": results["var95"], "var99": results["var99"]})


@app.route("/terminate", methods=["GET"])
def terminate():
    s = warmup_state["service"]

    if s != None:
        if s.lower() == "ec2":
            helper.terminate_ec2_instances()

    warmup_state["warm"] = False
    warmup_state["service"] = None
    warmup_state["terminated"] = True

    return jsonify({"result": "ok"})


@app.route("/scaled_terminated", methods=["GET"])
def scaled_terminate():
    ec2 = boto3.resource("ec2")
    if len(warmup_state["instances"]) == 0:
        return jsonify({"terminated": warmup_state["terminated"]})
    for instances in warmup_state["instances"]:
        instance = ec2.Instance(instances)
        if instance.state["Name"] != "terminated":
            warmup_state["terminated"] = False
            break
    return jsonify({"terminated": warmup_state["terminated"]})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
