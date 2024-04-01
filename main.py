from flask import Flask, request, jsonify, render_template
import boto3
import json
import helper
import os

app = Flask(__name__)

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
# Run one of this on the command line before running the code below:
# To create a secret with the AWS credentials in the Google Secret Manager
# gcloud secrets create aws-credentials  --data-file=C:\Users\Lawal\.aws\credentials --project=trading-signals-418515

# To Update the secret with the AWS credentials in the Google Secret Manager
# gcloud secrets versions add aws-credentials --data-file=C:\Users\Lawal\.aws\credentials --project=trading-signals-418515

# Authenticate with AWS
aws_credentials = helper.get_secret(
    project_id="trading-signals-418515", secret_id="aws-credentials"
)

try:
    lines = aws_credentials.split("\n")
    if len(lines) < 4:
        raise ValueError("Invalid AWS credentials format")

    aws_access_key_id = lines[1].split("=")[1].strip()
    aws_secret_access_key = lines[2].split("=")[1].strip()
    aws_session_token = lines[3].split("=")[1].strip()

except IndexError:
    print("Error: AWS credentials file is not in the expected format.")
except ValueError as ve:
    print(f"Error: {ve}")

# Configure boto3 with your AWS credentials
boto3.setup_default_session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
)

warmup_state = {"warm": False, "service": None, "terminated": True}


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

        # Count the instances running and ensure that there are no excess instances created if run multiple times
        if warmup_state["warm"] and warmup_state["service"] == s:
            return jsonify({"result": "ok"})
        # Store the service in the warmup_state
        warmup_state["service"] = s

        # Call the Lambda function
        lambda_client = boto3.client("lambda")

        input_params = {
            "service": s,
            "scale": r,
        }

        response = lambda_client.invoke(
            FunctionName="warmup_services",
            InvocationType="RequestResponse",
            Payload=json.dumps(input_params),
        )
        response_payload = json.load(response["Payload"])

        if response_payload["statusCode"] == 200:
            warmup_state["warm"] = True
            warmup_state["terminated"] = False
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify({"result": "ok", "lambda_response": response_payload})


@app.route("/scaled_ready", methods=["GET"])
def scaled_ready():
    return jsonify({"warm": warmup_state["warm"]})


@app.route("/terminate", methods=["GET"])
def terminate():
    s = warmup_state["service"]

    if s != None:
        if s.lower() == "ec2":
            helper.terminate_ec2_instances()
        elif s.lower() == "ecs":
            helper.terminate_ecs_services()
        elif s.lower() == "emr":
            helper.terminate_emr_clusters()
        else:
            pass

    warmup_state["warm"] = False
    warmup_state["service"] = None
    warmup_state["terminated"] = True

    return jsonify({"result": "ok"})


@app.route("/scaled_terminated", methods=["GET"])
def scaled_terminate():
    if not warmup_state["warm"]:
        return jsonify({"terminated": "true"})
    return jsonify({"terminated": "false"})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
