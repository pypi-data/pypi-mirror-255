import os
from urllib.parse import urlparse

import boto3
import botocore
from clickhouse_s3_etl_tools.exceptions.exception import S3Error
from clickhouse_s3_etl_tools.logger import get_logger
from clickhouse_s3_etl_tools.schema.schema_configs import S3Config

logger = get_logger(__name__)


class S3Connector:
    """
    Connector for interacting with Amazon S3.

    Args:
        s3_config (S3Config): Configuration for S3.

    Attributes:
        bucket_name (str): S3 bucket name.
        config (dict): S3 config
    """

    def __init__(self, s3_config: S3Config):
        """
        Initialize the S3Connector.

        Args:
            s3_config (S3Config): Configuration for S3.
        """
        parse_res = urlparse(s3_config.PATH_S3)
        path_segments = parse_res.path.lstrip("/").split("/")
        self.bucket_name = path_segments[0]
        self.sub_path = "/".join(path_segments[1:])
        self.config = {
            "aws_access_key_id": s3_config.S3_ACCESS_KEY,
            "aws_secret_access_key": s3_config.S3_SECRET_KEY,
            "endpoint_url": f"{parse_res.scheme}://{parse_res.netloc}",
            "service_name": "s3",
        }
        self.s3_client = None
        self.s3_resource = None

    def __enter__(self):
        """
        Enter the context manager.

        Returns:
            S3Connector: The S3Connector instance.
        """

        self.session = boto3.session.Session()
        self.s3_client = self.session.client(**self.config)
        self.s3_resource = self.session.resource(**self.config)

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.EndpointConnectionError,
        ):
            try:
                self.s3_client.list_buckets()
            except (
                botocore.exceptions.ClientError,
                botocore.exceptions.EndpointConnectionError,
            ) as e:
                raise S3Error(
                    url=self.config["endpoint_url"], message="Can't connect to S3"
                ) from e

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager.

        Args:
            exc_type: The type of exception.
            exc_val: The exception value.
            exc_tb: The exception traceback.
        """
        if self.s3_client is not None:
            self.s3_client.close()

    def do_nothing(self):
        pass

    def add_sub_path(self, directory: str):
        return f"{self.sub_path}/{directory}" if self.sub_path != "" else directory

    @staticmethod
    def dir_to_s3(path):
        if path.startswith("/"):
            path = path[1:]
        return os.path.join(path, "")

    def delete_dir(self, path):
        b = self.s3_resource.Bucket(self.bucket_name)
        b.objects.filter(Prefix=self.dir_to_s3(path)).delete()

    def path_exists(self, path):
        s3_dir = self.dir_to_s3(path)
        delim_num = s3_dir.count("/")
        b = self.s3_resource.Bucket(self.bucket_name)
        return (
            len(
                list(
                    (
                        f.key
                        for f in b.objects.filter(Prefix=s3_dir)
                        if f.key.count("/") == delim_num
                    )
                )
            )
            != 0
        )

    def get_file_list(self, parent_path):
        parent_path = self.add_sub_path(parent_path)
        s3_dir = self.dir_to_s3(parent_path)
        delim_num = s3_dir.count("/")
        b = self.s3_resource.Bucket(self.bucket_name)
        return list(
            (
                f.key
                for f in b.objects.filter(Prefix=s3_dir)
                if not f.key.endswith("/") and f.key.count("/") == delim_num
            )
        )

    def drop_table_directory_if_exists(self, file_directory: str):
        """
        Drop the S3 directory if it exists.

        Args:
             :param file_directory:
        """
        file_directory = self.add_sub_path(file_directory)

        if self.path_exists(file_directory):
            logger.info(f"Drop directory {file_directory} on S3 storage")
            self.delete_dir(file_directory)

    def create_bucket_if_not_exists(self):
        """
        Create the S3 bucket if it does not exist.
        """
        buckets = [t["Name"] for t in self.s3_client.list_buckets()["Buckets"]]

        if self.bucket_name not in buckets:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name, VersioningConfiguration={"Status": "Enabled"}
            )
