from flask import Flask, request, jsonify
import boto3
import json
import helper

app = Flask(__name__)

warmup_state = {"warm": False, "service": None, "terminated": True}


@app.route("/", methods=["GET"])
def home():
    # This is a simple home page, also doubles as a description of the API
    return jsonify("Welcome to the home page")


@app.route("/warmup", methods=["POST"])
def warmup():
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
