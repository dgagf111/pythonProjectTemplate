import pytest
from pathlib import Path

def pytest_collection_modifyitems(items):
    for item in items:
        if item.name == 'Test_Table':
            items.remove(item)

def pytest_collect_file(parent, file_path: Path):
    if file_path.name == "test_table.py":
        return None
