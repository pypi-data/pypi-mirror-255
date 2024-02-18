import re
import boto3
from enum import Enum
from typing import Optional
from datetime import date
from pydantic import BaseModel, field_validator
from .base import Base
from .s3 import stream_s3_file


s3 = boto3.client("s3")
athena = boto3.client("athena")
BUCKET_NAME = "yooncloud-temporary"

class Input(BaseModel):
    sql: str
    

class Athena(Base):
    def __init__(self, sql, *args, **kwargs):
        super().__init__(name="Athena", *args, **kwargs)
        self.input = Input(sql=sql)

    
    def gen(self):
        id = self.execute_query()
        key = f"athena/{id}.csv"
        s3.get_waiter('object_exists').wait(Bucket=BUCKET_NAME, Key=key)
        yield from stream_s3_file(bucket=BUCKET_NAME, key=key)


    def execute_query(self):
        response = athena.start_query_execution(
            QueryString=self.input.sql,
            QueryExecutionContext={
                "Database": "yooncloud",
            },
            ResultConfiguration={
                'OutputLocation': "s3://yooncloud-temporary/athena",
            },
            WorkGroup="yooncloud",
        )
        return response["QueryExecutionId"]
