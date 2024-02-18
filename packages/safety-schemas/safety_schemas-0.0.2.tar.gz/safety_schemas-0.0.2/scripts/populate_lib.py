from datetime import datetime
import inspect
import importlib
import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest
from pydantic.dataclasses import dataclass

DATA_DIR = "tests/models/lib"
MODULE_NAME = "safety_schemas.models"


for model, name in [(model, name) for name, model in inspect.getmembers(importlib.import_module(MODULE_NAME), inspect.isclass) if hasattr(model, "__annotations__")]:
    dir = Path() / DATA_DIR

    with open(dir / f"{name}_schema.json", 'w') as f:
        try:
            from pydantic import TypeAdapter
            adapter = TypeAdapter(model)
            schema = adapter.json_schema()
        except Exception as e:
            if hasattr(model, "timestamp"):      
                with patch.object(model.__pydantic_model__.__fields__["timestamp"], "default", datetime(2022, 1, 1, 0, 0, 0)):
                    schema = model.__pydantic_model__.schema()
            else:
                schema = model.__pydantic_model__.schema()

        json.dump(schema, f, indent=4)
