from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

@app.route("/get-ecr-token", methods=["POST"])
def get_ecr_token():
    data = request.get_json()

    aws_access_key = data.get("aws_access_key")
    aws_secret_key = data.get("aws_secret_key")
    region = data.get("region", "us-east-1")  # default region

    if not aws_access_key or not aws_secret_key:
        return jsonify({"error": "AWS access_key and secret_key are required"}), 400

    try:
        ecr_client = boto3.client(
            "ecr",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        response = ecr_client.get_authorization_token()
        token = response["authorizationData"][0]["authorizationToken"]

        return jsonify({"ecr_login_token": token})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

