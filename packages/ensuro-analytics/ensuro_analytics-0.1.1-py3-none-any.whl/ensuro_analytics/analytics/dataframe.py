"""
Creating pandas accessors to use the analytics functions directly from pandas
"""
import importlib
import pkgutil
import warnings
from pathlib import Path

from pandas.api.extensions import register_dataframe_accessor

# Use pathlib to get the path of the current file and then find the "metrics" subdirectory
current_dir = Path(__file__).parent
metrics_dir = current_dir / "metrics"

function_names = ["current_value", "time_series", "at_t"]


def create_accessor(module, accessor_name):
    class CustomAccessor:
        def __init__(self, pandas_obj):
            self._obj = pandas_obj
            # Ensure the DataFrame has the necessary columns
            if not all(col in self._obj.columns for col in module.REQUIRED_COLUMNS):
                raise ValueError(f"DataFrame must contain columns: {module.REQUIRED_COLUMNS}")

    def _create_method(func_name):
        def method(self, *args, **kwargs):
            subset = self._obj[list(module.REQUIRED_COLUMNS)]
            func = getattr(module, func_name)
            return func(subset, *args, **kwargs)

        return method

    # This loop ensures each function gets its own scope with the correct func_name
    for name in function_names:
        method = _create_method(name)
        method.__name__ = name
        setattr(CustomAccessor, name, method)

    register_dataframe_accessor(accessor_name)(CustomAccessor)


def create_ensuro_accessors():
    # Catch warning "UserWaning: registration of accessor ..."
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", category=UserWarning, message="registration of accessor")
        # Iterate through the metrics and create new modules
        for _, module_name, _ in pkgutil.iter_modules([str(metrics_dir)]):
            module = importlib.import_module(f".metrics.{module_name}", __package__)
            create_accessor(module, module_name)
