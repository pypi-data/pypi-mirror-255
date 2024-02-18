import boto3
from botocore.exceptions import ClientError
from .connection import Connection
import os
from loguru import logger


class AWSConnection(Connection):
    def __init__(self) -> None:
        super().__init__()
        self.session: boto3.session.Session = AWSConnection.connect(self)

    def connect(self) -> boto3.session.Session:
        """
        Base method for connecting to the data source.

        :return: The session object.
        """
        logger.info("Connecting to AWS session...")
        return self._get_session()

    def get_aws_secret(self, secret_name: str) -> str:
        """
        Method to retrieve a secret from AWS Secrets Manager.

        :param secret_name: The name of the secret to retrieve.

        :return: The secret value.
        """
        client: boto3.client = self.session.client(
            service_name="secretsmanager",
            region_name="us-east-1",
        )
        logger.info(
            f"Retrieving secret {secret_name} from AWS Secrets Manager..."
        )  # noqa
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            raise e

        secret = get_secret_value_response["SecretString"]
        return secret

    def _get_session(self) -> boto3.session.Session:
        """
        Method to retrieve the session object.

        :return: The session object.
        """
        if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            session = boto3.session.Session()
        else:
            session = boto3.session.Session(
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=os.environ.get("AWS_REGION_NAME"),
            )
        return session
