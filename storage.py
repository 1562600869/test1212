import copy
import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path


def get_data_path():
    home = Path.home()
    return home / ".orchard.json"


def get_lock_path():
    return get_data_path().with_suffix(".lock")


def default_db():
    return {
        "trees": {},
        "sprays": [],
        "harvests": [],
        "sales": [],
    }


def _read_raw(path):
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


def load():
    return _read_raw(get_data_path())


def save(data):
    path = get_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


@contextmanager
def transaction(need_write=True):
    """
    带文件锁的 JSON 事务上下文：
    - 进入：加排他锁，读取最新数据，做一份快照用于回滚
    - 成功退出：原子写盘
    - 异常退出：丢弃内存改动，不写盘
    """
    lock_path = get_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        db = _read_raw(get_data_path())
        snapshot = copy.deepcopy(db) if need_write else None
        try:
            yield db
            if need_write:
                save(db)
        except Exception:
            if need_write and snapshot is not None:
                db.clear()
                db.update(snapshot)
            raise
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)
