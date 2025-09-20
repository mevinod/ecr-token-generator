from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

@app.route("/get-token", methods=["POST"])
def get_token():
    data = request.get_json()

    aws_access_key = data.get("aws_access_key") if data else None
    aws_secret_key = data.get("aws_secret_key") if data else None
    region = data.get("region") if data else "us-east-1"

    if not aws_access_key or not aws_secret_key:
        return jsonify({"error": "Missing AWS credentials"}), 400

    try:
        client = boto3.client(
            "ecr",
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
        response = client.get_authorization_token()
        token = response["authorizationData"][0]["authorizationToken"]
        return jsonify({"token": token})
    except (BotoCoreError, ClientError) as e:
        return jsonify({"error": f"Unable to get ECR token: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
