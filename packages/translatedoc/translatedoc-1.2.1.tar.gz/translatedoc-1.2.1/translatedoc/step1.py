#!/usr/bin/env python3
"""テキスト抽出部分だけ切り出したもの。"""

import argparse
import logging
import os
import pathlib
import sys

import tqdm
from markdownify import markdownify as md

from translatedoc import utils

logger = logging.getLogger(__name__)


def main():
    """メイン関数。"""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Extract text from documents.")
    parser.add_argument(
        "--output-dir",
        "-o",
        default=pathlib.Path("."),
        type=pathlib.Path,
        help="output directory (default: .)",
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="overwrite existing files"
    )
    parser.add_argument(
        "--strategy",
        "-s",
        choices=["auto", "fast", "ocr_only", "hi_res"],
        default=os.environ.get("TRANSLATEDOC_STRATEGY", "hi_res"),
        help="document partitioning strategy (default: hi_res)",
        # hi_resはtesseractやdetectron2を使うので重いけど精度が高いのでデフォルトに
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")
    parser.add_argument("input_files", nargs="+", help="input files/URLs")
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exit_code = 0
    for input_file in tqdm.tqdm(args.input_files, desc="Input files/URLs"):
        input_path = pathlib.Path(input_file)
        try:
            # テキスト抽出
            tqdm.tqdm.write(f"Loading {input_file}...")
            text = extract_text(input_file, args.strategy)
            source_path = args.output_dir / input_path.with_suffix(".Source.txt").name
            if utils.check_overwrite(source_path, args.force):
                source_path.parent.mkdir(parents=True, exist_ok=True)
                source_path.write_text(text, encoding="utf-8")
                tqdm.tqdm.write(f"{source_path} written.")
        except Exception as e:
            logger.error(f"{e} ({input_file})")
            exit_code = 1

    sys.exit(exit_code)


def extract_text(input_file: str | pathlib.Path, strategy: str = "auto"):
    """テキスト抽出。

    Args:
        input_file: 入力ファイルパスまたはURL。
        strategy: ドキュメント分割戦略。

    """
    # timmのimport時にSegmentation Faultが起きることがあるようなのでとりあえず暫定対策
    # https://github.com/invoke-ai/InvokeAI/issues/4041
    os.environ["PYTORCH_JIT"] = "0"

    input_file = str(input_file)
    kwargs = (
        {"url": input_file}
        if input_file.startswith("http://") or input_file.startswith("https://")
        else {"filename": input_file}
    )

    with tqdm.tqdm.external_write_mode():
        from unstructured.chunking.title import chunk_by_title
        from unstructured.documents.elements import Text as TextElement
        from unstructured.partition.auto import partition

        elements = partition(
            **kwargs,
            strategy=strategy,
            skip_infer_table_types=[],
            pdf_infer_table_structure=True,
        )

    # テーブルをTextElement化
    for i, el in enumerate(elements):
        if (
            el is not None
            and el.category == "Table"
            and el.metadata is not None
            and el.metadata.text_as_html is not None
        ):
            elements[i] = TextElement(
                text=md(el.metadata.text_as_html.strip()), metadata={}
            )
    chunks = chunk_by_title(
        elements, combine_text_under_n_chars=0, max_characters=128000
    )

    return "\n\n".join(str(c).strip() for c in chunks) + "\n"


if __name__ == "__main__":
    main()
