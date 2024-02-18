import re
import boto3
from enum import Enum
from typing import Optional
from datetime import date
from pydantic import BaseModel, field_validator
from .base import Base
from .athena import Athena


s3 = boto3.client("s3")

class Column(str, Enum):
    stockcode = "stockcode"
    date = "date"
    name = "name"
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    amount = "amount"
    stocks = "stocks"
    market = "market"
    change = "change"


class Input(BaseModel):
    start_date: date
    end_date: date
    columns: Optional[list[Column]]
    modified_price: bool

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, v:date):
        # koreadaychart 데이터는 1996년 5월 2일부터 시작한다.
        assert v.toordinal() >= date.fromisoformat("1996-05-02").toordinal(), "'start_date' must be equal or greater than 1996-05-02"
        return v
    

class Koreadaychart(Base):
    def __init__(
            self,
            start_date:str,
            end_date:str,
            columns=["stockcode", "date", "name", "open", "high", "low", "close", "volume", "amount", "stocks", "market", "change"],
            modified_price=False, 
            *args,
            **kwargs,
        ):
        full_schema = {
            "stockcode": "string",
            "date": "date",
            "name": "string",
            "open": "int",
            "high": "int",
            "low": "int",
            "close": "int",
            "volume": "int",
            "amount": "int",
            "stocks": "int",
            "market": "string",
            "change": "float",
        }
        schema = {k:v for k,v in full_schema.items() if k in columns}
        super().__init__(name="Koreadaychart", schema=schema, *args, **kwargs)
        self.input = Input(start_date=start_date, end_date=end_date, columns=columns, modified_price=modified_price)

    
    def gen(self):
        columns = ", ".join(self.input.columns)
        sql = f"""
            select {columns}
            from koreadaychart
            where timestamp >= '{self.input.start_date}' and timestamp <= '{self.input.end_date}'
        """
        yield from Athena(sql=sql)