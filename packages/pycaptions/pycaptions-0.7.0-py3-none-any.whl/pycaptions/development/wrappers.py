import io

from ..options import style_options
from ..microTime import MicroTime as MT

def captionsDetector(func):
    def wrapper(content):
        if not isinstance(content, io.IOBase):
            if not isinstance(content, str):
                raise ValueError("The content is not a unicode string or I/O stream.")
            content = io.StringIO(content)
        offset = content.tell()
        result = func(content=content)
        content.seek(offset)
        return result
    return wrapper


def captionsWriter(extension: str, generator_type: str = None, new_line: str = "\n"):
    def decorator(func):
        def wrapper(self, filename: str, languages: list[str] = None, **kwargs):
            filename = self.makeFilename(filename=filename, extension=getattr(self.extensions, extension),
                                         languages=languages, **kwargs)
            encoding = kwargs.get("file_encoding") or "UTF-8"
            languages = languages or [self.default_language]

            if "lines" in kwargs:
                lines = kwargs["lines"]
                del kwargs["lines"]
            else:
                lines = style_options.lines

            if "new_line" in kwargs:
                line_separator = kwargs["new_line"]
            else:
                line_separator = new_line

            if "style" in kwargs:
                style_name = kwargs["style"]
            else:
                style_name = style_options.style

            if kwargs.get("generator"):
                generator = kwargs.get("generator")
            else:
                if style_name == "full":
                    generator = (((getattr(data.get_style(i), generator_type)(lines=lines, options=self.options, **kwargs) for i in languages), data) for data in self)
                else:
                    if style_name != None:
                        so = "', '".join(style_options.style_option)
                        print(f"Invalid style option {style_name}. Expected: None '{so}'")
                    generator = (((line_separator.join(data.get(lang=i, lines=lines, **kwargs)) for i in languages), data) for data in self)
            try:
                with open(filename, "w", encoding=encoding) as file:
                    func(self=self, filename=filename, languages=languages, generator=generator, file=file, **kwargs)
            except IOError as e:
                print(f"I/O error({e.errno}): {e.strerror}")
            except Exception as e:
                print(f"Error {e}")

        return wrapper
    return decorator


def captionsReader(func):
    """
    Decorator for captions readers

    Parameters:
    - content (str | io.IOBase): Content of file or string
    - languages (list[str], optional): list of languages (default self.default_language)
    - time_offset (MicroTime, optional): Used for shifting time on read (default is 0)
    """
    def wrapper(self, content: str | io.IOBase, languages: list[str] = None,
                time_offset: MT = None, **kwargs):
        if not isinstance(content, io.IOBase):
            if not not isinstance(content, str):
                raise ValueError("The content is not a unicode string or I/O stream.")
            content = io.StringIO(content)
        languages = languages or [self.default_language]
        time_offset = kwargs.get("time_offset") or MT()
        func(self, content, languages, **kwargs)
        self.shift_time(time_offset)

    return wrapper
