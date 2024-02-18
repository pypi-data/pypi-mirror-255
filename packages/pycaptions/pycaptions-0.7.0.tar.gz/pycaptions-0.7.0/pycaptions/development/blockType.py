class BlockType:
    """
    Enum for BlockType
    """
    CAPTION = 1
    COMMENT = 2
    STYLE = 3
    LAYOUT = 4
    METADATA = 5

    @classmethod
    def getvars(cls) -> dict:
        """
        Used to retrive all indexes for specific block type.
        """
        return {attr: getattr(cls, attr) for attr in dir(cls)
                if not callable(getattr(cls, attr)) and not attr.startswith("__")}