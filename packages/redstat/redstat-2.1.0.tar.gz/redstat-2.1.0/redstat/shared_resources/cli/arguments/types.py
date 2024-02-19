from argparse import FileType
from pathlib import Path

output_file_type = FileType('w', encoding='utf-8')


def output_dir_type(folder_name) -> Path:
    folder = Path(folder_name)
    folder.mkdir(parents=True, exist_ok=True)
    return folder
