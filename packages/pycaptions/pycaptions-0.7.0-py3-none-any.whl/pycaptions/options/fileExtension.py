class FileExtensions:
    SRT = ".srt"
    SUB = ".sub"
    TTML = ".ttml"
    VTT = ".vtt"

    @classmethod
    def getvars(cls) -> dict:
        """
        Used to retrive all extensions for specific format.
        """
        return {attr: getattr(cls, attr) for attr in dir(cls)
                if not callable(getattr(cls, attr)) and not attr.startswith("__")}