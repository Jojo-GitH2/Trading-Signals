from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    # This is a simple home page, also doubles as a description of the API
    return jsonify("Welcome to the home page")


@app.route("/warmup", methods=["POST"])
def warmup():
    data = request.get_json()
    s = data.get("service")
    r = data.get("scale")

    # Warmup Logic will be rewritten here
    return jsonify({"result": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
