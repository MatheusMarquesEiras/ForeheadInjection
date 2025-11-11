import os
from pathlib import Path

def file_exist(file_path: Path):
    if os.path.isfile(str(file_path.absolute())):
        return 'active'
    else:
        return 'disable'