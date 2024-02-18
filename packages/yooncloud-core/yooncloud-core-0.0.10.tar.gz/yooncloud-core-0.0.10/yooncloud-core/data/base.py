from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, create_model

class Base:
    def __init__(self, schema=None, name="", transform=[]):
        self.transform = transform
        self.model = self.create_model(schema, name) if schema else None
        

    def __iter__(self):
        gen = self.gen()
        gen = self._transform(gen)
        for a in gen:
            if self.model:
                a = self.model(**a)
            yield a


    def _transform(self, gen):
        for t in self.transform:
            # 원래는 `transform` 인자로 주어진 함수들(예를들면 sort, map, filter 등)을 사용해서 데이터를 변형시킨뒤 내보낸다는 컨셉인데 확실히 필요한 기능인지 어떤지 몰라서 일단 구현은 안함
            pass
        return gen

    
    def create_model(self, schema:Optional[dict], name:str) -> BaseModel:
        for key, value in schema.items():
            if value == "string":
                schema[key] = (str, ...)
            elif value == "int" or value == "integer":
                schema[key] = (int, ...)
            elif value == "float":
                schema[key] = (float, ...)
            elif value == "date":
                schema[key] = (date, ...)
            elif value == "datetime":
                schema[key] = (datetime, ...)
        return create_model(name, **schema)


    def gen(self):
        raise NotImplementedError()