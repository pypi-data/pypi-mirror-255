from json import dump
from typing import TextIO


def save_json(obj: list[dict], file: TextIO):
    with file:
        dump(obj, file, indent=2, ensure_ascii=False)
