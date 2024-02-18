import io
import re

from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT


STYLE_PATERN = re.compile(r"::cue\((#[^)]+)\)")


@staticmethod
@captionsDetector
def detectVTT(content: str | io.IOBase) -> bool:
    """
    Used to detect WebVTT caption format.

    It returns True if:
     - the first line starts with `WebVTT`
    """
    if content.readline().rstrip().startswith("WEBVTT"):
        return True
    return False


@captionsReader
def readVTT(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    metadata = Block(BlockType.METADATA, id="default")
    content.readline()
    line = content.readline().strip()
    while line:
        line = line.split(": ", 1)
        metadata.options[line[0]] = line[1]
        line = content.readline().strip()
    self.addMetadata("default", metadata)

    line = content.readline()
    style_block_count = 0
    while line:
        line = line.strip()
        if line.startswith("NOTE"):
            temp = line.split(" ", 1)
            comment = Block(BlockType.COMMENT)
            if len(temp) > 1:
                comment.append(temp[1])
            line = content.readline().strip()
            while line:
                comment.append(line)
                line = content.readline().strip()
            self.options["blocks"].append(comment)
        elif line == "STYLE":
            style_block_count += 1
            style = ""
            line = content.readline().strip()
            while line:
                style += line
                line = content.readline().strip()

            def replace_style(match):
                if match.group(1).startswith("#"):
                    if match.group(1) in self.options["style_metadata"]["identifier_to_new"]:
                        return self.options["style_metadata"]["identifier_to_new"][match.group(1)]
                    self.options["style_metadata"]["style_id_counter"] += 1
                    style_name = f"#style{self.options['style_metadata']['style_id_counter']}"
                    self.options["style_metadata"]["identifier_to_original"][style_name] = match.group(1)
                    self.options["style_metadata"]["identifier_to_new"][match.group(1)] = style_name
                    return style_name
                return match.group(1)
            self.addStyle(str(style_block_count), Block(BlockType.STYLE, id=str(style_block_count),
                                                        style=re.sub(STYLE_PATERN, replace_style, style)))
        elif line == "REGION":
            line = content.readline().strip()
            temp = dict()
            while line:
                line = line.split(":", 1)
                temp[line[0]] = line[1]
                line = content.readline().strip()
            if temp.get("width"):
                temp["width"] = int(temp["width"][:-1])/100.0
            if temp.get("lines"):
                temp["lines"] = int(temp["lines"])
            if temp.get("regionanchor"):
                ra = temp["regionanchor"].split(",")
                temp["regionanchor"] = [int(ra[0][:-1])/100.0, int(ra[1][:-1])/100.0]
            if temp.get("viewportanchor"):
                vp = temp["viewportanchor"].split(",")
                temp["viewportanchor"] = [int(vp[0][:-1])/100.0, int(vp[1][:-1])/100.0]
            self.addLayout(temp["id"], Block(BlockType.LAYOUT, id=temp["id"], layout=temp))
        else:
            break
        line = content.readline()

    while line:
        if line.startswith("NOTE"):
            temp = line.split(" ", 1)
            comment = Block(BlockType.COMMENT)
            if len(temp) > 1:
                comment.append(temp[1])
            line = content.readline().strip()
            while line:
                comment.append(line)
                line = content.readline().strip()
            self.append(comment)
        else:
            caption = Block(BlockType.CAPTION)
            if "-->" not in line:
                caption.options["id"] = line.strip()
                line = content.readline().strip()
            start, end = line.split(" --> ", 1)
            end = end.split(" ", 1)
            if len(end) > 1:
                caption.options["style"] = end[1]
            caption.start_time = MT.fromVTTTime(start)
            caption.end_time = MT.fromVTTTime(end[0])
            counter = 1
            line = content.readline().strip()
            if line.startswith("{"):
                caption.block_type = BlockType.METADATA
            while line:
                if len(languages) > 1:
                    caption.append(line, languages[counter])
                    counter += 1
                else:
                    caption.append(line, languages[0])
                line = content.readline().strip()
            self.append(caption)
        line = content.readline()


@captionsWriter("VTT", "getVTT")
def saveVTT(self, filename: str, languages: list[str] = None, generator: list = None, 
            file: io.FileIO = None, **kwargs):
    file.write("WEBVTT\n\n")
    index = 1
    for text, data in generator:
        if data.block_type != BlockType.CAPTION:
            continue
        elif index != 1:
            file.write("\n\n")
        file.write(f"{data.start_time.toVTTTime()} --> {data.end_time.toVTTTime()}\n")
        file.write("\n".join(i for i in text))
        index += 1
