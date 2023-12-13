import importlib
import json
import pathlib
import time
import typing as t
from os import path

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
            return {
                "type": "BaseModel",
                "model_class": f"{output.__class__.__module__}.{output.__class__.__qualname__}",
                "value": output.dict(),
            }
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
    def deserialize_from_json(filename):
        filepath = path.join(pathlib.Path(__file__).parent, "data", filename)
        with open(filepath, "r") as fp:
            data = json.load(fp)

        input_args = []
        for input_arg in data["input"]["args"]:
            _input_arg = Record._deserialize(input_arg)
            input_args.append(_input_arg)
        data["input"]["args"] = input_args

        input_kwargs = []
        for input_kwarg in data["input"]["kwargs"]:
            _input_kwarg = Record._deserialize(input_kwarg)
            input_kwarg.append(_input_kwarg)
        data["input"]["kwargs"] = input_kwargs

        output = Record._deserialize(data["output"])
        data["output"] = output
        return data

    @classmethod
    def _deserialize(self, data):
        if data["type"] == "DataFrame":
            return pd.DataFrame.from_dict(data.output)
        elif data["type"] == "BaseModel":
            return self._get_base_model_instance(
                model_class=data["model_class"],
                value=data["value"],
            )
        elif data["type"] == "float":
            return float(data["value"])
        elif data["type"] == "int":
            return int(data["value"])
        elif data["type"] == "str":
            return str(data["value"])
        elif data["type"] == "None":
            return None
        else:
            raise Exception(f"Un-implemented deserialization for type {data['type']}")

    @staticmethod
    def _get_base_model_instance(
        model_class: str, value: t.Dict[str, t.Any]
    ) -> pydantic.BaseModel:
        class_parts = model_class.split(".")
        class_name = class_parts[-1]
        module_path = ".".join(class_parts[0:-1])
        module = importlib.import_module(module_path)
        _class = getattr(module, class_name)
        instance = _class.parse_obj(value)
        return instance
