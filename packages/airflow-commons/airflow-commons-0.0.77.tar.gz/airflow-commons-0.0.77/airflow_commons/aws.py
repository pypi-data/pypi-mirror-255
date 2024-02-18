import time
import botocore
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

from s3transfer import S3UploadFailedError

from airflow_commons.internal.athena.core import (
    query,
    add_partitions,
    get_query_execution,
)
from airflow_commons.internal.util.time_utils import get_interval_duration
from airflow_commons.logger import get_logger
from s3fs import S3FileSystem


class S3FileSystemOperator(object):
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_CONTENT_TYPE = "str"

    def __init__(self, key: str = None, secret: str = None):
        """
        Initializes s3FileSystemOperator instance with given credentials.
        If no credentials were supplied, uses environment variables.

        :param key:
        :param secret:
        """
        self.s3_file_system = S3FileSystem(key=key, secret=secret)
        self.logger = get_logger("S3FileSystemOperator")

    def write_into_s3_file(
        self,
        bucket_name: str,
        file_name: str,
        data,
        content_type: str = DEFAULT_CONTENT_TYPE,
        retry_count: int = DEFAULT_RETRY_COUNT,
    ):
        """
        Writes the given string data into the specified file in the specified bucket.
        If file does not exist creates one, if exists overrides it.

        :param bucket_name: Name of the bucket that the target file is stored
        :param file_name: Name of the file that will be overridden
        :param data: An object contains the content of the file
        :param content_type: A string that describes the type of the contents of the file, can take values "str", "pyarrow.lib.Table" and "bytes"
        :param retry_count: retry count for S3 upload equals to three on default
        """
        writing_start = datetime.now()
        total_upload_tries = 0
        if content_type == "pyarrow.lib.Table":
            output_file = f"s3://{bucket_name}/{file_name}"
            pq.write_table(
                table=data, where=output_file, filesystem=self.s3_file_system
            )
        else:
            write_mode = "w"
            if content_type == "bytes":
                write_mode = "wb"
            while total_upload_tries <= retry_count:
                with self.s3_file_system.open(
                    bucket_name + "/" + file_name, write_mode
                ) as f:
                    try:
                        f.write(data)
                        break
                    except botocore.exceptions.NoCredentialsError as e:
                        total_upload_tries = total_upload_tries + 1
                        if total_upload_tries == retry_count:
                            self.logger.error(
                                f"Writing into {bucket_name}/{file_name} failed because of missing credentials, traceback {e}"
                            )
                            raise e
                        time.sleep(1)
        writing_end = datetime.now()
        self.logger.debug(
            f"Writing finished in {get_interval_duration(writing_start, writing_end)} seconds"
        )

    def write_to_s3_with_parquet(
        self, bucket_name: str, container_name: str, table: pa.Table
    ):
        """
        Writes the given string data into the specified file in the specified bucket.
        :param bucket_name: Name of the bucket that the target file is stored
        :param container_name: Name of the container that will be overridden
        :param table: Table that will be written to the dataset whose filepath created by bucket_name and container_name
        """
        output_file = f"s3://{bucket_name}/{container_name}"
        pq.write_to_dataset(
            table=table, root_path=output_file, filesystem=self.s3_file_system
        )

    def move_s3_file(
        self,
        source_path: str,
        destination_path: str,
        retry_count: int = DEFAULT_RETRY_COUNT,
    ):
        """
        Move the file in the source path to the destination path. If the file does not exist in the specified
        source path, it raises a FileNotFoundError.
        If the aws key and secret is not given, method uses the environmental variables as credentials.

        :param source_path: The path where the file locates
        :param destination_path: The path where the file will be moved
        :param retry_count: retry count for S3 moving equals to three on default
        """
        moving_start = datetime.now()
        total_move_tries = 0
        while total_move_tries <= retry_count:
            try:
                self.s3_file_system.move(source_path, destination_path)
                break
            except botocore.exceptions.NoCredentialsError as e:
                total_move_tries = total_move_tries + 1
                if total_move_tries == retry_count:
                    self.logger.error(
                        f"Reading from {source_path} to {destination_path} failed because of missing credentials, traceback {e}"
                    )
                    raise e
                time.sleep(1)
        moving_end = datetime.now()
        self.logger.debug(
            f"Moving finished in {get_interval_duration(moving_start, moving_end)} seconds"
        )

    def read_from_s3_file(
        self,
        bucket_name: str,
        file_name: str,
        retry_count: int = DEFAULT_RETRY_COUNT,
    ):
        """
        Read data from the specified file in the specified bucket.
        If file does not exists it raises a FileNotFoundError.
        If the aws key and secret is not given, method uses the environmental variables as credentials.

        :param bucket_name: Name of the bucket that the target file is stored
        :param file_name: Name of the file that will be read
        :param retry_count: retry count for S3 reading equals to three on default
        :return: content of the target file in string format
        """
        reading_start = datetime.now()
        total_read_tries = 0
        while total_read_tries <= retry_count:
            with self.s3_file_system.open(bucket_name + "/" + file_name, "rb") as f:
                try:
                    data = f.read()
                    break
                except botocore.exceptions.NoCredentialsError as e:
                    total_read_tries = total_read_tries + 1
                    if total_read_tries == retry_count:
                        self.logger.error(
                            f"Reading from {bucket_name}/{file_name} failed because of missing credentials, traceback {e}"
                        )
                        raise e
                    time.sleep(1)
        reading_end = datetime.now()
        self.logger.debug(
            f"Reading finished in {get_interval_duration(reading_start, reading_end)} seconds"
        )
        return data.decode("utf-8")


class S3Operator(object):
    def __init__(self, key: str = None, secret: str = None):
        """
        Initializes S3Operator instance with given credentials.
        If no credentials are supplied, uses environment variables

        :param key: AWS access key id, default is None
        :param secret: AWS secret access key, default is None
        """
        self.client = boto3.client(
            service_name="s3",
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        self.logger = get_logger("S3Operator")

    def upload_file_to_s3_bucket(
        self, path_to_file: str, bucket_name: str, file_name: str
    ):
        """
        Uploads the given file to the given s3 bucket.

        :param path_to_file: Path to file that will be uploaded to s3 bucket.
        :param bucket_name: Name of the bucket that file will be uploaded to.
        :param file_name: Name of the file (key of the file in s3).
        """
        upload_start = datetime.now()
        try:
            self.client.upload_file(path_to_file, bucket_name, file_name)
        except S3UploadFailedError as e:
            self.logger.error(f"Upload to {bucket_name} failed")
            raise e
        upload_end = datetime.now()
        self.logger.debug(
            f"Upload finished in {get_interval_duration(upload_start, upload_end)} seconds"
        )


class AthenaOperator(object):
    def __init__(
        self,
        result_bucket: str,
        result_folder: str,
        key: str = None,
        secret: str = None,
    ):
        """
        Initializes AthenaOperator instance with given credentials. If no credentials are supplied, uses environment variables
        :param result_bucket: Result bucket name
        :param result_folder: Result folder name
        :param key: AWS access key id, default is None
        :param secret: AWS secret access key, default is None
        """
        self.result_bucket = result_bucket
        self.result_folder = result_folder
        self.client = boto3.client(
            "athena",
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        self.logger = get_logger("AthenaOperator")

    def run_athena_query(
        self,
        sql: str,
        database: str,
    ):
        """
        Runs given query on Athena using AthenaClient
        :param sql: Query to run
        :param database: Database name
        """
        return query(
            client=self.client,
            sql=sql,
            result_bucket=self.result_bucket,
            result_folder=self.result_folder,
            database=database,
        )

    def add_partitions(self, database: str, table: str, partitions: list):
        """
        Prepares and runs a DML query to add given partitions to Athena table
        :param database: Database name
        :param table: Table name
        :param partitions:  List of partitions to be added
        """
        return add_partitions(
            client=self.client,
            result_bucket=self.result_bucket,
            result_folder=self.result_folder,
            database=database,
            table=table,
            partitions=partitions,
        )

    def get_query_execution(self, query_execution_id: str):
        """
        Returns current state of an athena query
        :param query_execution_id: Unique execution id of the query
        """
        return get_query_execution(self.client, query_execution_id)
