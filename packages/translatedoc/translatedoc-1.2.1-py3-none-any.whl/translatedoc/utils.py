"""ユーティリティ関数置き場。"""

import pathlib
import sys

import tqdm


def check_overwrite(output_path: pathlib.Path, force: bool) -> bool:
    """上書き確認。"""
    if output_path.exists() and not force:
        with tqdm.tqdm.external_write_mode():
            print(f"Output path already exists: {output_path}", file=sys.stderr)
            try:
                input_ = input("Overwrite? [y/N] ")
            except EOFError:
                input_ = ""
            if input_ != "y":
                print("Skipped.", file=sys.stderr)
                return False
    return True
