from flask import Flask, request, jsonify, render_template
import boto3
import json
import helper
import os
import time

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
        # Get the input parameters
        data = request.get_json()
        s = data.get("service")
        r = data.get("scale")

        # #Cand ensure that there are no excess instances created if run multiple times
        # if warmup_state["warm"] and warmup_state["service"] == s:
        #     return jsonify({"result": "ok"})
        # Store the service in the warmup_state
        warmup_state["service"] = s
        warmup_state["scale"] = r

        # Call the Lambda function
        lambda_client = boto3.client("lambda")

        input_params = {
            "service": s,
            "scale": r,
        }

        start_time = time.time()
        response = lambda_client.invoke(
            FunctionName="warmup_services",
            InvocationType="RequestResponse",
            Payload=json.dumps(input_params),
        )

        end_time = time.time()
        warmup_state["warmup_time"] = end_time - start_time
        response_payload = json.load(response["Payload"])

        if response_payload["statusCode"] == 200:
            warmup_state["warm"] = True
            warmup_state["terminated"] = False
            warmup_state["instances"] = response_payload["instances"]
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


@app.route("/analyse", methods=["POST"])




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
