import importlib
import json
import os
import pathlib
import time
import typing as t
from os import path

import pandas as pd
import pydantic


def get_time():
    return int(time.time() * 1000)


class Record:
    """
    Records the input and output of the decorated function.
    Only stores the inputs with named args (kwargs).
    The kwargs can be excluded from recording adding the kwarg name to the excluded_kwargs list
    """

    def __init__(self, enabled=True, excluded_kwargs: t.Optional[t.List[str]] = None):
        self.enabled = enabled
        self.excluded_kwargs = excluded_kwargs or []

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
            input_dict = self._build_input_dict(kwargs)
            output_dict = self._serialize(output)
            data = {
                "time": now,
                "function": function_name,
                "input": input_dict,
                "output": output_dict,
            }
            self._save(data, now, function_name)
        except Exception as e:
            print(f"Error recording function {function_name}: {e}")

    def _build_input_dict(self, kwargs) -> t.Dict[str, t.Any]:
        input_dict = {}
        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name in self.excluded_kwargs:
                continue
            input_dict[kwarg_name] = self._serialize(kwarg_value)
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
        prefix = time.strftime("%y%m%d")
        filepath = path.join(
            pathlib.Path(__file__).parent, "data", f"{prefix}-{now}-{function}.json"
        )
        with open(filepath, "w") as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def _deserialize_from_json(filename):

        try:
            filepath = path.join(pathlib.Path(__file__).parent, "data", filename)
            with open(filepath, "r") as fp:
                data = json.load(fp)

            for kwarg_name, kwarg_value in data["input"].items():
                value = Record._deserialize(kwarg_value)
                data["input"][kwarg_name] = value

            output = Record._deserialize(data["output"])
            data["output"] = output
            return data
        except Exception as err:
            print(f"Error deserializing from {filename}: {err}")
            raise err

    @classmethod
    def _deserialize(self, data: t.Dict[str, t.Any]):
        data_type = data["type"]
        data_value = data["value"]
        if data_type == "DataFrame":
            return pd.read_json(data_value)
        elif data_type == "BaseModel":
            return self._get_base_model_instance(
                model_class=data["model_class"],
                value=data_value,
            )
        elif data_type == "float":
            return float(data_value)
        elif data_type == "int":
            return int(data_value)
        elif data_type == "str":
            return str(data_value)
        elif data_type == "None":
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

    @staticmethod
    def load_all_recorded_data():
        """
        Traverse the data directory, deserialize all json files in it,
        and stores the result in dict indexed by function name,
        inside every function there is a list with all recorded inputs and outputs
        """

        dir_path = path.join(pathlib.Path(__file__).parent, "data").__str__()
        recorded_data = {}
        for filename in os.listdir(dir_path):
            print(f"Loading recorded data from {filename} ...")
            if filename.endswith(".json"):
                data = Record._deserialize_from_json(filename)
                function_name = data["function"]
                if function_name in recorded_data:
                    recorded_data[function_name].append(data)
                else:
                    recorded_data[function_name] = [data]
        return recorded_data
