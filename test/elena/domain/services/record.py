import json
import pathlib
import time

import pandas as pd
import pydantic


def get_time():
    return int(time.time() * 1000)


class Record:

    def __init__(self, enabled=True):
        self.enabled = enabled

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            if self.enabled:
                self._record(kwargs, output, func.__name__)
            return output

        return wrapper

    def _record(self, kwargs, output, function_name):
        try:
            now = get_time()
            output_type, serialized_output = self._serialize(output)
            data = {
                "time": now,
                "function": function_name,
                "input": kwargs,
                "output": serialized_output,
                "output_type": output_type,
            }
            self._save(data, now, function_name)
        except Exception as e:
            print(f"Error recording function {function_name}: {e}")

    @staticmethod
    def _serialize(output):

        if isinstance(output, pd.DataFrame):
            return "DataFrame", output.to_json()
        elif isinstance(output, pydantic.BaseModel):
            return "BaseModel", output.dict()
        elif isinstance(output, float):
            return "float", output
        elif isinstance(output, int):
            return "int", output
        elif isinstance(output, str):
            return "str", output
        elif not output:
            return "None", None
        else:
            raise Exception(f"Un-implemented serialization for type {type(output)}")

    @staticmethod
    def _save(data, now, function):
        directory = pathlib.Path(__file__).parent.__str__()
        prefix = time.strftime("%y%m%d")
        filepath = f"{directory}/data/{prefix}-{now}-{function}.json"
        with open(filepath, "w") as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def deserialize_from_json(filepath):
        with open(filepath, "r") as fp:
            data = json.load(fp)

        return Record._deserialize(data)

    @classmethod
    def _deserialize(self, data):
        if data["output_type"] == "DataFrame":
            return pd.DataFrame.from_dict(data["output"])
        elif data["output_type"] == "BaseModel":
            return pydantic.BaseModel(**data["output"])
        elif data["output_type"] == "float":
            return float(data["output"])
        elif data["output_type"] == "int":
            return int(data["output"])
        elif data["output_type"] == "str":
            return str(data["output"])
        elif data["output_type"] == "None":
            return None
        else:
            raise Exception(f"Un-implemented deserialization for type {data['output_type']}")
