import io

from bs4 import BeautifulSoup
from ..development import Block, BlockType, captionsDetector, captionsReader, captionsWriter
from ..microTime import MicroTime as MT


@staticmethod
@captionsDetector
def detectTTML(content: str | io.IOBase) -> bool:
    """
    Used to detect Timed Text Markup Language caption format.

    It returns True if:
     - the first non empty line starts with `<?xml` and contains `<tt xml` OR
     - the first non empty line starts with `<tt xml` OR
     - the second non empty line starts with `<tt xml`
    """
    line = content.readline()
    while line:
        if line.lstrip():
            break
        line = content.readline()
    if line.startswith("<tt xml") or line.startswith("<?xml") and "<tt xml" in line:
        return True
    line = content.readline()
    while line:
        if line.lstrip():
            break
        line = content.readline()
    if line.startswith("<tt xml"):
        return True
    return False


# ttp:frameRate, ttp:frameRateMultiplier, ttp:subFrameRate, ttp:tickRate, ttp:timeBase
@captionsReader
def readTTML(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
    content = BeautifulSoup(content, "xml")
    if len(languages) == 1 and languages[0] == "und":
        if content.tt.get("xml:lang"):
            languages = [content.tt.get("xml:lang")]
            self.setDefaultLanguage(languages[0])
    for index, langs in enumerate(content.body.find_all("div")):
        lang = langs.get("xml:lang")
        p_start, p_end = MT.fromTTMLTime(langs.get("begin"), langs.get("dur"), langs.get("end"))
        for block, line in enumerate(langs.find_all("p")):
            start, end = MT.fromTTMLTime(line.get("begin"), line.get("dur"), line.get("end"))
            start += p_start
            end += p_start
            if start > p_end:
                start = p_end
                end = p_end
            elif end > p_end:
                end = p_end
            
            if index == 0:
                caption = Block(BlockType.CAPTION, start_time=start, end_time=end)
            else:
                caption = self[block]
            for lang_index, text in enumerate(line.get_text().strip().split("\n")):
                if len(languages) > 1:
                    caption.append(text, lang or languages[lang_index])
                else:
                    caption.append(text, lang or languages[0])
            if index == 0:
                self.append(caption)


@captionsWriter("TTML", "getTTML", "<br/>")
def saveTTML(self, filename: str, languages: list[str] = None, generator: list = None, 
             file: io.FileIO = None, **kwargs):
    mark_language_type = kwargs.get("mark_language_type") or False

    def createMarkedLine():
        for index, t in enumerate(text):
            p = content.new_tag("p", begin=begin, end=end)
            p.append(BeautifulSoup(t,"html.parser"))
            lang[index].append(p)

    def createLine():
        p = content.new_tag("p", begin=begin, end=end)
        p.append(BeautifulSoup("<br/>".join(i for i in text),"html.parser"))
        lang[0].append(p)

    content = BeautifulSoup("""<?xml version="1.0" encoding="utf-8"?>
                            <tt xmlns="http://www.w3.org/ns/ttml">
                            <body></body>
                            </tt>""", "xml")
    body = content.select_one("body")
    lang = []
    
    if mark_language_type:
        for i in languages:
            lang.append(content.new_tag("div"))
            lang[-1]["xml:lang"] = i
            body.append(lang[-1])
        line = createMarkedLine
    else:
        lang.append(content.new_tag("div"))
        body.append(lang[-1])
        line = createLine

    for text, data in generator:
        if data.block_type != BlockType.CAPTION:
            continue
        begin = data.start_time.toTTMLTime()
        end = data.end_time.toTTMLTime()
        line()

    file.write(content.prettify())
