import boto3
import psycopg2
from sqlalchemy import create_engine

from maisaedu_utilities_prefect.dw import get_red_credentials
from .Types import DEV, LOCAL, IAM_ROLE


class Connector:
    def __init__(self, env, s3_credentials, source_credentials, target_credentials):
        self.source_credentials = source_credentials
        self.target_credentials = target_credentials
        self.s3_credentials = s3_credentials
        self.env = env
        self.iam_role = IAM_ROLE

    def connect_target(self):
        if self.target_credentials is None:
            if self.env == LOCAL:
                env = DEV
            else:
                env = self.env

            red_credentials = get_red_credentials(env)
        else:
            red_credentials = self.target_credentials

        self.target_conn = psycopg2.connect(
            host=red_credentials["host"],
            database=red_credentials["database"],
            user=red_credentials["user"],
            password=red_credentials["password"],
            port=red_credentials["port"],
        )

        self.target_conn.autocommit = True

    def close_target(self):
        self.target_conn.close()

    def connect_s3(self):
        session = boto3.Session(
            aws_access_key_id=self.s3_credentials["access-key"],
            aws_secret_access_key=self.s3_credentials["secret-access-key"],
            region_name=self.s3_credentials["region"],
        )

        self.s3_session = session.resource("s3")

    def connect_source(self):
        engine = create_engine(
            f"postgresql+psycopg2://{self.source_credentials['user']}:{self.source_credentials['password']}@{self.source_credentials['host']}:{self.source_credentials['port']}/{self.source_credentials['database']}"
        )
        self.source_conn = engine.connect().execution_options(stream_results=True)

    def close_source(self):
        self.source_conn.close()
