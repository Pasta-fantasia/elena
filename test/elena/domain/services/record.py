import json
import os
import pathlib
import time
import typing as t
from os import path

import pandas as pd
import pydantic

from elena.shared.dynamic_loading import get_class


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
            input_dict = self._build_input_dict(kwargs)
            output_dict = self._serialize(output)
            data = {
                "function": function_name,
                "input": input_dict,
                "output": output_dict,
            }
            self._save(data, function_name)
        except Exception as err:
            print(f"Error recording function {function_name}: {err}")

    def _build_input_dict(self, kwargs) -> t.Dict[str, t.Any]:
        input_dict = {}
        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name in self.excluded_kwargs:
                continue
            input_dict[kwarg_name] = self._serialize(kwarg_value)
        return input_dict

    @staticmethod
    def _serialize(output) -> t.Dict[str, t.Any]:

        model_class = f"{output.__class__.__module__}.{output.__class__.__qualname__}"
        if isinstance(output, pd.DataFrame):
            return {"type": "DataFrame", "value": output.to_json()}
        elif isinstance(output, pydantic.BaseModel):
            return {
                "type": "BaseModel",
                "model_class": model_class,
                "value": output.dict(),
            }
        elif isinstance(output, dict):
            return {"type": "dict", "value": output}
        elif isinstance(output, list):
            return {"type": "dict", "value": output}
        elif model_class == "builtins.float":
            return {"type": "float", "value": output}
        elif model_class == "builtins.int":
            return {"type": "int", "value": output}
        elif model_class == "builtins.str":
            return {"type": "str", "value": output}
        elif not output:
            return {"type": "None", "value": output}
        else:
            return {
                "type": "OtherModel",
                "model_class": model_class,
                "value": output,
            }

    @staticmethod
    def _save(data, function):
        now = get_time()
        filepath = path.join(pathlib.Path(__file__).parent, "data", f"{function}-{now}.json")
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
        elif data_type == "dict":
            return data_value
        elif data_type == "list":
            return data_value
        elif data_type == "float":
            return float(data_value)
        elif data_type == "int":
            return int(data_value)
        elif data_type == "str":
            return str(data_value)
        elif data_type == "None":
            return None
        elif data_type == "OtherModel":
            return self._get_other_model_instance(
                model_class=data["model_class"],
                value=data_value,
            )
        else:
            raise Exception(f"Un-implemented deserialization for type {data['type']}")

    @staticmethod
    def _get_base_model_instance(model_class: str, value: t.Dict[str, t.Any]) -> pydantic.BaseModel:
        try:
            _class = get_class(model_class)
            instance = _class.parse_obj(value)
            return instance
        except Exception as err:
            print(f"Error deserializing Pydantic base model class '{model_class}' with value '{value}': {err}")
            raise err

    @staticmethod
    def _get_other_model_instance(model_class: str, value: t.Dict[str, t.Any]) -> pydantic.BaseModel:
        try:
            _class = get_class(model_class)
            instance = _class(value)
            return instance
        except Exception as err:
            print(f"Error deserializing other model class '{model_class}' with value '{value}': {err}")
            raise err

    @staticmethod
    def load_all_recorded_data() -> t.Dict[str, t.Any]:
        """
        Traverse the data directory, deserialize all json files in it,
        and stores the result in dict indexed by function name,
        inside every function there is a list with all recorded inputs and outputs
        """

        dir_path = path.join(pathlib.Path(__file__).parent, "data").__str__()
        recorded_data: t.Dict[str, t.Any] = {}
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

    @staticmethod
    def load_recorded_output(function_name: str, all_recorded_data: t.Dict[str, t.Any], **kwargs):
        if function_name not in all_recorded_data:
            raise RuntimeError(f"Cannot find recorded data for function '{function_name}'")
        records = all_recorded_data[function_name]

        errors: t.List[str] = []
        for record in records:
            match = True
            errors = []
            for recorded_kwarg_name, recorded_kwarg_value in record["input"].items():
                if Record._record_matches_kwargs(recorded_kwarg_name, recorded_kwarg_value, kwargs):
                    continue
                else:
                    match = False
                    errors.append(
                        f"recorded kwarg '{recorded_kwarg_name}' with value '{recorded_kwarg_value}' "
                        f"does not match '{kwargs}'\n"
                    )
                    break
            if match:
                return record["output"]
        raise RuntimeError(
            f"Cannot find recorded output for function '{function_name}' " f"with kwargs {kwargs}: \n{errors}"
        )

    @staticmethod
    def _record_matches_kwargs(recorded_kwarg_name, recorded_kwarg_value, kwargs) -> bool:
        if recorded_kwarg_name not in kwargs:
            return False

        if kwargs[recorded_kwarg_name] == recorded_kwarg_value:
            return True
        return False
