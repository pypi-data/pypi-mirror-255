import os


home = os.path.expanduser("~")

STORAGE_BASE = os.environ.get("AGENTIC_STORAGE_DIR", f"{home}/.agentic")

DATA_BASE = os.path.join(STORAGE_BASE, "data")


def local_data_path(dir_name: str) -> str:
    dir_path = os.path.join(DATA_BASE, dir_name)
    return dir_path
