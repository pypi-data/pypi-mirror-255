import io
import re

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT


@staticmethod
@captionsDetector
def detectLRC(content: str | io.IOBase) -> bool:
    r"""
    Used to detect Synchronized Accessible Media Interchange caption format.

    It returns True if:
     - the first line starts with `[` and ends with `]` OR
     - ^\[(\d{1,3}):(\d{1,2}(?:[:.]\d{1,3})?)\]
    """
    line = content.readline().strip()
    if line.startswith("[") and line.endswith("]") or re.match(r"^\[(\d{1,3}):(\d{1,2}(?:[:.]\d{1,3})?)\]", line):
        return True
    return False

@captionsReader
def readLRC(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    raise ValueError("Not Implemented")


@captionsWriter("LRC", "getLRC")
def saveLRC(self, filename: str, languages: list[str] = None, generator: list = None, 
            file: io.FileIO = None, **kwargs):
    raise ValueError("Not Implemented")
