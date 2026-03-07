import boto3
import argparse
import json
from botocore.exceptions import ClientError

class AWSSecretsManager:
    def __init__(self, region_name="us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region_name)

    def create_secret(self, secret_name, secret_value):
        """Creates or updates a secret in AWS Secrets Manager."""
        try:
            if isinstance(secret_value, (dict, list)):
                secret_string = json.dumps(secret_value)
            else:
                secret_string = str(secret_value)
                
            response = self.client.create_secret(
                Name=secret_name,
                SecretString=secret_string
            )
            return True, response
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                # Update existing secret
                response = self.client.put_secret_value(
                    SecretId=secret_name,
                    SecretString=secret_string
                )
                return True, response
            return False, str(e)

    def get_secret(self, secret_name):
        """Retrieves a secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if "SecretString" in response:
                return True, response["SecretString"]
            return False, "Secret not found or no string value."
        except ClientError as e:
            return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Manage AWS Secrets Manager (Alternative Product for A/B Testing)")
    parser.add_argument("--name", required=True, help="The name of the secret")
    parser.add_argument("--value", help="The value of the secret (required for create/update)")
    parser.add_argument("--get", action="store_true", help="Retrieve the secret")
    parser.add_argument("--region", default="us-east-1", help="AWS Region")

    args = parser.parse_args()
    sm = AWSSecretsManager(region_name=args.region)

    if args.get:
        success, value = sm.get_secret(args.name)
        if success:
            print(f"Secret: {args.name}\nValue: {value}")
        else:
            print(f"Error: {value}")
    elif args.value:
        success, response = sm.create_secret(args.name, args.value)
        if success:
            print(f"Secret '{args.name}' saved successfully in AWS Secrets Manager.")
        else:
            print(f"Error: {response}")
    else:
        print("Specify either --value (to set) or --get (to retrieve).")

if __name__ == "__main__":
    main()
