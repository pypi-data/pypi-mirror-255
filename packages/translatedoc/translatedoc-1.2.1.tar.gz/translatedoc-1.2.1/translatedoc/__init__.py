"""translatedocをライブラリとして使うとき用。"""

from .step1 import extract_text
from .step2 import partition, split_with_separator, translate

__all__ = ["extract_text", "split_with_separator", "partition", "translate"]
