import os
from pathlib import Path

def file_exist(file_path: Path):
    return os.path.isfile(str(file_path.absolute()))