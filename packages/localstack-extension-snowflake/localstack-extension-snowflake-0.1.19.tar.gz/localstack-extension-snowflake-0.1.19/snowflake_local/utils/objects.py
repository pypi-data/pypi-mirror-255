import importlib
from typing import Any
def get_full_class_name(obj):A=obj.__class__;return f"{A.__module__}.{A.__name__}"
def load_class(class_name):A,E,B=class_name.rpartition('.');C=importlib.import_module(A);D=getattr(C,B);return D