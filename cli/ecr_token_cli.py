#!/usr/bin/env python3
import argparse
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import sys

def get_ecr_token(access_key, secret_key, region="us-east-1"):
    try:
        client = boto3.client(
            "ecr",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        response = client.get_authorization_token()
        token = response["authorizationData"][0]["authorizationToken"]
        return token
    except (BotoCoreError, ClientError) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Get AWS ECR login token")
    parser.add_argument("--access-key", required=True, help="AWS Access Key ID")
    parser.add_argument("--secret-key", required=True, help="AWS Secret Access Key")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")

    args = parser.parse_args()

    token = get_ecr_token(args.access_key, args.secret_key, args.region)
    print(token)

if __name__ == "__main__":
    main()
