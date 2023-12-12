import json
import pathlib
import time
import typing as t

import pandas as pd
import pydantic


def get_time():
    return int(time.time() * 1000)


class Record:

    def __init__(self, enabled=True, excluded_args: t.Optional[t.List[str]] = None):
        self.enabled = enabled
        self.excluded_args = excluded_args or []

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            if self.enabled:
                self._record(args, kwargs, output, func.__name__)
            return output

        return wrapper

    def _record(self, args, kwargs, output, function_name):
        try:
            now = get_time()
            output_dict = self._serialize(output)
            input_dict = self._build_input_dict(args, kwargs)
            data = {
                "time": now,
                "function": function_name,
                "input": input_dict,
                "output": output_dict,
            }
            self._save(data, now, function_name)
        except Exception as e:
            print(f"Error recording function {function_name}: {e}")

    def _build_input_dict(self, args, kwargs) -> t.Dict[str, t.Any]:
        input_dict = {"args": [], "kwargs": kwargs}
        for arg in args:
            if arg.__class__.__name__ in self.excluded_args:
                continue
            input_dict["args"].append(self._serialize(arg))
        return input_dict

    @staticmethod
    def _serialize(output) -> t.Dict[str, t.Any]:

        if isinstance(output, pd.DataFrame):
            return {"type": "DataFrame", "value": output.to_json()}
        elif isinstance(output, pydantic.BaseModel):
            return {"type": "BaseModel", "class": f"{output.__class__.__module__}.{output.__class__.__qualname__}", "value": output.dict(),}
        elif isinstance(output, float):
            return {"type": "float", "value": output}
        elif isinstance(output, int):
            return {"type": "int", "value": output}
        elif isinstance(output, str):
            return {"type": "str", "value": output}
        elif not output:
            return {"type": "None", "value": output}
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
