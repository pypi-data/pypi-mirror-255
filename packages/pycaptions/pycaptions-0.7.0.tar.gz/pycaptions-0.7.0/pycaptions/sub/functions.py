import io
import re
import langcodes 

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT
from ..styling import Styling


PATTERN = r"\{.*?\}"


@staticmethod
@captionsDetector
def detectSUB(content: str | io.IOBase) -> bool:
    r"""
    Used to detect MicroDVD caption format.

    It returns True if:
     - the start of a first line in a file matches regex `^{\d+}{\d+}`
    """
    line = content.readline()
    if re.match(r"^{\d+}{\d+}", line) or line.startswith(r"{DEFAULT}"):
        return True
    return False


@captionsReader
def readSUB(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    if not self.options.get("frame_rate"):
        self.options["frame_rate"] = kwargs.get("frame_rate") or 25
    frame_rate = kwargs.get("frame_rate") or self.options.get("frame_rate")

    if not self.options.get("blocks"):
        self.options["blocks"] = []

    if "micro_dvd" not in self.options:
        self.options["micro_dvd"] = {
            "control_codes": dict(),
            "counter": 0
        }

    line = content.readline().strip()
    while line:
        if line.startswith(r"{DEFAULT}"):
            self.options["blocks"].append(Block(BlockType.STYLE, style=line))
        else:
            lines = line.split("|")
            params = re.findall(PATTERN, lines[0])
            start = MT.fromSUBTime(params[0].strip("{} "), frame_rate)
            end = MT.fromSUBTime(params[1].strip("{} "), frame_rate)
            caption = Block(BlockType.CAPTION, start_time=start, end_time=end)
            for counter, line in enumerate(lines):
                line = Styling.fromSUB(line, PATTERN, self.options["micro_dvd"]) 
                if len(languages) > 1:
                    caption.append(line, languages[counter])
                else:
                    caption.append(line, languages[0])
            self.append(caption)
        line = content.readline().strip()

    if "language" in self.options["micro_dvd"]:
        self.add_metadata("default", Block(BlockType.METADATA, id="default", 
                                           Language=langcodes.find(self.options["micro_dvd"]["language"]).language))

    if not self.options["micro_dvd"]["control_codes"]:
        del self.options["micro_dvd"]


@captionsWriter("SUB", "getSUB", "|")
def saveSUB(self, filename: str, languages: list[str] = None, generator: list = None, 
            file: io.FileIO = None, **kwargs):
    frame_rate = kwargs.get("frame_rate") or self.options.get("frame_rate") or 25
    index = 1
    for text, data in generator:
        if data.block_type != BlockType.CAPTION:
            continue
        elif index != 1:
            file.write("\n")
        file.write("{"+data.start_time.toSUBTime(frame_rate)+"}{"+data.end_time.toSUBTime(frame_rate)+"}")
        file.write("|".join(i for i in text))
        index += 1
