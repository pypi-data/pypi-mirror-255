import io

from .development import CaptionsFormat


class Captions(CaptionsFormat):
    """
    Captions

    A generic class to read different types of caption formats.

    Example:

    with Captions("path/to/file.srt") as captions:
        captions.saveSRT("file")
    """
    def __init__(self, filename: str = None, default_language: str = "und", **options):
        super().__init__(filename, default_language, **options)

    # from .lrc.functions import detectLRC, saveLRC, readLRC
    # from .sami.functions import detectSAMI, saveSAMI, readSAMI
    from .srt.functions import detectSRT, saveSRT, readSRT
    from .sub.functions import detectSUB, saveSUB, readSUB
    from .ttml.functions import detectTTML, saveTTML, readTTML
    # from .usf.functions import detectUSF, saveUSF, readUSF
    from .vtt.functions import detectVTT, saveVTT, readVTT

    readers = {
        # "lrc": readLRC,
        # "sami": readSAMI,
        "srt": readSRT,
        "sub": readSUB,
        "ttml": readTTML,
        # "usf": readUSF,
        "vtt": readVTT
    }

    savers = {
        # "lrc": saveLRC,
        # "sami": saveSAMI,
        "srt": saveSRT,
        "sub": saveSUB,
        "ttml": saveTTML,
        "dfxp": saveTTML,
        "xml": saveTTML,
        # "usf": saveUSF,
        "vtt": saveVTT
    }

    detectors = {
        "srt": detectSRT,
        "vtt": detectVTT,
        "ttml": detectTTML,
        "sub": detectSUB,
        # "sami": detectSAMI,
        # "usf": detectUSF,
        # "lrc": detectLRC
    }

    def get_format(self, file: str | io.IOBase) -> str | None:
        for format, detector in self.detectors.items():
            if detector(file):
                self.fileFormat = format
                return format
        return self.fileFormat

    def detect(self, content: str | io.IOBase) -> bool:
        if not self.get_format(content):
            return False
        return True

    def read(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
        format = self.get_format(content)
        if not format:
            return
        self.readers[format](self, content, languages, **kwargs)

    def save(self, filename: str, languages: list[str] = None, output_format: str = None, **kwargs):
        if output_format:
            output_format = output_format.lstrip(".").lower()
        else:
            output_format = self.fileFormat
        if output_format not in self.savers:
            raise ValueError(f"Incorect output format {output_format}")
        self.savers[output_format](self, filename=filename, languages=languages, **kwargs)
