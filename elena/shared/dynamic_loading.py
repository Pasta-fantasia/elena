import importlib


def get_class(class_path: str):
    """Get class from class path"""
    try:
        class_parts = class_path.split(".")
        class_name = class_parts[-1]
        module_path = ".".join(class_parts[0:-1])
        module = importlib.import_module(module_path)
        _class = getattr(module, class_name)
    except Exception as err:
        raise Exception(f"Error loading class '{class_path}': {err}")
    return _class


def get_instance(class_path: str):
    _class = get_class(class_path)
    return _class()
