import json
import os
from pathlib import Path


def get_data_path():
    home = Path.home()
    return home / ".orchard.json"


def default_db():
    return {
        "trees": {},
        "sprays": [],
        "harvests": [],
        "sales": [],
    }


def load():
    path = get_data_path()
    if not path.exists():
        return default_db()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in default_db():
            if key not in data:
                data[key] = default_db()[key]
        return data
    except (json.JSONDecodeError, OSError):
        return default_db()


def save(data):
    path = get_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
