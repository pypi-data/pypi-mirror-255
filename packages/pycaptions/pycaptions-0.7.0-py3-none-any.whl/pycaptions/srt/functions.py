import io

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT

from ..styling import Styling


@staticmethod
@captionsDetector
def detectSRT(content: str | io.IOBase) -> bool:
    """
    Used to detect SubRip caption format.

    It returns True if:
     - the first line is a number 1
     - the second line contains a `-->`
    """
    if content.readline().rstrip() == "1" and '-->' in content.readline():
        return True
    return False


def convertFromSRTLayout(self, id, layout, width, height):
    layout = layout.split(" ")
    if len(layout) != 4:
        print(f"Error converting layout: Excpected 4 arguments got {len(layout)}")
        return
    for i, v in enumerate(["X1", "X2", "Y1", "Y2"]):
        if layout[i][2:] != v:
            print(f"Error converting layout: Invalid field at position {i} expected {v} got {layout[0][2:]}")
            return
    try:
        x1 = int(layout[0][3:])
        x2 = int(layout[1][3:])
        y1 = int(layout[2][3:])
        y2 = int(layout[3][3:])
        self.addLayout(id, Block(BlockType.LAYOUT, id=id, layout={
                "width": (x2-x1) / width,
                "height": (y2-y1) / height,
                "viewportanchor": [x1 / width, y1 / height],
                "regionanchor": [0, 0]
                }))
    except Exception as e:
        print(f"Error converting layout: {e}")
        return


def getSRTLayout(self, id, width, height):
    layout = self.getLayout(id)
    if not layout:
        return ""
    x1 = layout.options["layout"]["viewportanchor"][0] * width
    x2 = layout.options["layout"]["width"] * width + x1
    y1 = layout.options["layout"]["viewportanchor"][1] * height
    y2 = layout.options["layout"]["height"] * height + y1
    return f" X1:{x1} X2:{x2} Y1:{y1} Y2:{y2}"


@captionsReader
def readSRT(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    """
    kwargs:
     - media_width (int, optional): Used for extended SRT coordinates conversion
     - media_height (int, optional): Used for extended SRT coordinates conversion
    """
    width = kwargs.get("media_width") or self.media_width
    height = kwargs.get("media_height") or self.media_height

    counter = 0
    id = content.readline()
    while id:
        start, end = content.readline().split(" --> ")
        end = end.strip().split(" ", 1)

        caption = Block(BlockType.CAPTION, languages[0], MT.fromSRTTime(start),
                        MT.fromSRTTime(end[0]))
        if len(end) == 2:
            convertFromSRTLayout(self, id.strip(), end[1], width, height)
        line = content.readline().strip()
        while line:
            if len(languages) > 1:
                caption.append(Styling.fromSRT(line), languages[counter])
                counter += 1
            else:
                caption.append(Styling.fromSRT(line), languages[0])
            line = content.readline().strip()
        self.append(caption)
        id = content.readline()


@captionsWriter("SRT", "getSRT")
def saveSRT(self, filename: str, languages: list[str] = None, generator: list = None,
            file: io.FileIO = None, **kwargs):
    """
    kwargs:
     - srt_extended (bool, optional): Used to make extended version of SRT (default is False)
     - media_width (int, optional): Used for extended SRT coordinates conversion
     - media_height (int, optional): Used for extended SRT coordinates conversion
    """
    width = kwargs.get("media_width") or self.media_width
    height = kwargs.get("media_height") or self.media_height
    isExtended = kwargs.get("srt_extended") or False
    extended = ""
    index = 1
    for text, data in generator:
        if data.block_type != BlockType.CAPTION:
            continue
        elif index != 1:
            file.write("\n\n")
        if isExtended:
            extended = getSRTLayout(self, index, width, height)
        file.write(f"{index}\n")
        file.write(f"{data.start_time.toSRTTime()} --> {data.end_time.toSRTTime()}{extended}\n")
        file.write("\n".join(i for i in text))
        index += 1
