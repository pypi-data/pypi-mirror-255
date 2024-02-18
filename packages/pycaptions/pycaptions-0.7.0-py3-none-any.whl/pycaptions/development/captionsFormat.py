import json
import io
import os
import copy

from langcodes import standardize_tag, tag_is_valid
from charset_normalizer import detect as detect_encoding
from .block import Block, BlockType
from ..microTime import MicroTime as MT
from ..options import FileExtensions, save_extensions


JSON_VERSION = 1


class CaptionsFormat:
    """
    Represents a format for handling captions in a multimedia context.

    Attributes:
        extensions (FileExtensions): An instance of the FileExtensions class for managing file extensions.

    Methods:
        setDefaultLanguage: Set the default language for captions.
        insert: Insert a block at the specified index.
        detect: Detect the format of the captions file.
        read: Read captions from content.
        checkContent: Check if the content is valid type.
        save: Save captions to a file.
        makeFilename: Adds languages and extension to filename.
        append: Append a Block to the list of blocks.
        shift_time: Shift the timing of all blocks by the specified duration.
        shift_start: Shift the start time of all blocks by the specified duration.
        shift_end: Shift the end time of all blocks by the specified duration.
        fromJson: Load captions format from a JSON file.
        toJson: Save captions format to a JSON file.
        join: Joins another CaptionsFormat class data.
        joinFile: Joins CaptionsFormat data from file.
        __getitem__: Retrieve the block at the specified index.
        __setitem__: Set the block at the specified index.
        __str__: Return a string representation of the captions format.
        __iadd__: In-place addition for concatenating blocks.
        __isub__: In-place subtraction for removing blocks in a specific language.
        __iter__: Iterator for iterating through blocks.
        __len__: Return the number of blocks in the captions format.
        __enter__: Enter the context for managing resources.
        __exit__: Exit the context, handling exceptions.
    """

    def __init__(self, file_name_or_content: str = None, default_language: str = "und",
                 time_length: MT = None, file_extensions: FileExtensions = None,
                 media_height: int = None, media_width: int = None, isFile: bool = True,
                 legacyJson: bool = False, **options):
        """
        Initialize a new instance of CaptionsFormat class.

        Parameters:
        - file_name_or_content (str, optional): The name of the file or file content/string associated with the captions, used for "with" keyword (default is None).
        - isFile (str, bool): Defines if file_name_or_content parameter is file name, used for "with" keyword (default is True).
        - default_language (str, optional): The default language for captions (default is "und" for undefined).
        - **options: Additional keyword arguments for customization (e.g. metadata, style, ...).
        """
        self.json_version = options.get("json_version") or JSON_VERSION
        self.time_length = time_length or MT()
        self.file_name_or_content = file_name_or_content
        self.isFile = isFile
        self.legacyJson = legacyJson
        self.media_height = media_height or 1080
        self.media_width = media_width or 1920
        self.options = options or {}
        if not self.options.get("blocks"):
            self.options["blocks"] = []
        if not self.options.get("layout"):
            self.options["layout"] = dict()
        if not self.options.get("style"):
            self.options["style"] = dict()
        if not self.options.get("metadata"):
            self.options["metadata"] = dict()
        if not self.options.get("style_metadata"):
            self.options["style_metadata"] = dict()
        if not self.options["style_metadata"].get("identifier_to_original"):
            self.options["style_metadata"]["identifier_to_original"] = dict()
        if not self.options["style_metadata"].get("identifier_to_new"):
            self.options["style_metadata"]["identifier_to_new"] = dict()
        if not self.options["style_metadata"].get("style_id_counter"):
            self.options["style_metadata"]["style_id_counter"] = 0
        self._block_list: list[Block] = []
        self.setDefaultLanguage(default_language)
        self.extensions = file_extensions or save_extensions

    def __getitem__(self, index: int):
        return self._block_list[index]

    def __setitem__(self, index: int, value: Block):
        self._block_list[index] = value

    def __delitem__(self, index: int):
        del self._block_list[index]

    def __iadd__(self, value):
        if not isinstance(value, CaptionsFormat):
            raise ValueError("Unsupported type. Must be an instance of `CaptionsFormat`")
        for i, value in enumerate(value):
            if i < len(self._block_list):
                self._block_list[i] += value
            else:
                self.append(value)
        return self

    def __isub__(self, language: str):
        for value in self._block_list:
            value -= language
        return self

    def __iter__(self):
        return iter(self._block_list)

    def __str__(self):
        return "\n".join(f"{i}. {caption}" for i, caption in enumerate(self._block_list))

    def __enter__(self):
        encoding = self.options.get("encoding") or "UTF-8"
        if self.isFile:
            _, ext = os.path.splitext(self.file_name_or_content)
            if ext == ".json":
                if self.legacyJson:
                    self.fromLegacyJson(self.file_name_or_content, encoding=encoding)
                else:
                    self.fromJson(self.file_name_or_content, encoding=encoding)
            else:
                if encoding == "auto":
                    encoding = self.getEncoding(self.file_name_or_content)
                with open(self.file_name_or_content, "r", encoding=encoding) as stream:
                    if self.detect(stream):
                        languages = self.getLanguagesFromFilename(self.file_name_or_content)
                        if languages and self.default_language == "und":
                            self.setDefaultLanguage(languages[0])
                        self.read(stream, languages)
        else:
            if self.detect(self.file_name_or_content):
                self.read(self.file_name_or_content)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __len__(self):
        return len(self._block_list)

    def sort(self):
        self.removeComments()
        self.sort(key=lambda x: x.start_time)

    def removeOptionsComments(self):
        index = 0
        while index < len(self.options["blocks"]):
            if self.options["blocks"].block_type == BlockType.COMMENT:
                del self[index]
            else:
                index += 1

    def removeComments(self):
        index = 0
        while index < len(self):
            if self[index].block_type == BlockType.COMMENT:
                del self[index]
            else:
                index += 1

    def removeAllComments(self):
        self.removeComments()
        self.removeOptionsComments()

    def setOptionsBlockId(self, index1, index2):
        block = self.options["blocks"][index1]
        if block.type == BlockType.LAYOUT:
            self.options["layout"][block.options["id"]] = index2
        elif block.type == BlockType.STYLE:
            self.options["style"][block.options["id"]] = index2
        elif block.type == BlockType.METADATA:
            self.options["metadata"][block.options["id"]] = index2

    def swapOptionsBlock(self, index1: int, index2: int):
        if index1 == index2 or index1 < 0 or index2 < 0:
            return
        self.setOptionsBlockId(index1, index2)
        self.setOptionsBlockId(index2, index1)
        self.options["blocks"][index1], self.options["blocks"][index2] = self.options["blocks"][index2], self.options["blocks"][index1]

    def deleteOptionsBlock(self, index: int):
        block = self.options["blocks"][index]
        if block.type == BlockType.LAYOUT:
            del self.options["layout"][block.options["id"]]
        elif block.type == BlockType.STYLE:
            del self.options["style"][block.options["id"]]
        elif block.type == BlockType.METADATA:
            del self.options["metadata"][block.options["id"]]
        del self.options["blocks"][index]

    def addLayout(self, id: str, layout: Block):
        if layout.block_type != BlockType.LAYOUT:
            raise ValueError(f"Expected BlockType {BlockType.METADATA} got {layout.block_type}")
        self.options["blocks"].append(layout)
        self.options["layout"][id] = len(self.options["blocks"])-1

    def getLayout(self):
        return (self.options["blocks"][i] for i in self.options["layout"].values())

    def getLayoutById(self, id: str):
        if id in self.options["layout"]:
            return self.options["blocks"][self.options["layout"][id]]
        return None

    def addStyle(self, id: str, style: Block):
        if style.block_type != BlockType.STYLE:
            raise ValueError(f"Expected BlockType {BlockType.METADATA} got {style.block_type}")
        self.options["blocks"].append(style)
        self.options["style"][id] = len(self.options["blocks"])-1

    def getStyle(self):
        return (self.options["blocks"][i] for i in self.options["style"].values())

    def getStyleById(self, id: str):
        if id in self.options["style"]:
            return self.options["blocks"][self.options["style"][id]]
        return None

    def addMetadata(self, id: str, metadata: Block):
        if metadata.block_type != BlockType.METADATA:
            raise ValueError(f"Expected BlockType {BlockType.METADATA} got {metadata.block_type}")
        self.options["blocks"].append(metadata)
        self.options["metadata"][id] = len(self.options["blocks"])-1

    def getMetadata(self):
        return (self.options["blocks"][i] for i in self.options["metadata"].values())

    def getMetadataById(self, id: str):
        if id in self.options["metadata"]:
            return self.options["blocks"][self.options["metadata"][id]]
        return None

    def setDefaultLanguage(self, language: str):
        standardized = standardize_tag(language, macro=True)
        self.default_language = standardized if tag_is_valid(standardized) else "und"

    def insert(self, index: int, value: Block):
        self._block_list.insert(index, value)

    def detect(self, file: str | io.IOBase = None):
        raise ValueError("Not implemented")

    def read(self, content: str | io.IOBase, languages: list[str] = None, **kwargs):
        raise ValueError("Not implemented")

    def save(self, filename: str, languages: list[str] = None, **kwargs):
        raise ValueError("Not implemented")

    def makeFilename(self, filename: str, extension: str, languages: list[str] = None,
                     include_languages_in_filename: bool = True, **kwargs):
        languages = languages or [self.default_language]
        if filename.endswith(extension):
            file, _ = os.path.splitext(filename)
        else:
            file = filename
        if include_languages_in_filename:
            file = ".".join((val for val in file.split('.') if val not in languages))+"."+".".join(languages)

        return file+extension

    @staticmethod
    def getFilename(filename: str, directory: str = None):
        if not directory:
            directory = os.path.dirname(filename)
        filename, _ = os.path.splitext(os.path.basename(filename))
        filename = filename.split(".")
        if len(filename) > 1:
            clean_filename = []
            for i in filename:
                try:
                    if tag_is_valid(standardize_tag(i, macro=True)):
                        continue
                    else:
                        clean_filename.append(i)
                except Exception:
                    clean_filename.append(i)
            if clean_filename:
                return os.path.join(directory, ".".join(clean_filename))
        return os.path.join(directory, ".".join(filename))

    @staticmethod
    def getLanguagesFromFilename(filename: str):
        filename, _ = os.path.splitext(os.path.basename(filename))
        filename = filename.split(".")
        if len(filename) > 1:
            languages = []
            for i in filename:
                try:
                    if tag_is_valid(standardize_tag(i, macro=True)):
                        languages.append(i)
                except Exception:
                    continue
            if not languages:
                return None
        else:
            return None
        return languages

    @staticmethod
    def getLanguagesAndFilename(filename: str, directory: str = None):
        if not directory:
            directory = os.path.dirname(filename)
        filename, _ = os.path.splitext(os.path.basename(filename))
        filename = filename.split(".")
        if len(filename) > 1:
            languages = []
            clean_filename = []
            for i in filename:
                try:
                    if tag_is_valid(standardize_tag(i, macro=True)):
                        languages.append(i)
                except Exception:
                    clean_filename.append(i)
            if not languages:
                languages = None
            if clean_filename:
                return languages, os.path.join(directory, ".".join(clean_filename))
        return languages, os.path.join(directory, ".".join(filename))

    def append(self, item: Block):
        if item.end_time and item.end_time > self.time_length:
            self.time_length = item.end_time
        self._block_list.append(item)

    def shift_time(self, time: MT):
        for i in self:
            if i.block_type == BlockType.CAPTION:
                i.shift_time(time)

    def shift_start(self, time: MT):
        for i in self:
            if i.block_type == BlockType.CAPTION:
                i.shift_time(time)

    def shif_end(self, time: MT):
        for i in self:
            if i.block_type == BlockType.CAPTION:
                i.shift_time(time)

    def _loadJson(self, data, **kwargs):
        self.time_length = data["time_length"]
        self.default_language = data["default_language"]
        self.filename = data["filename"]
        self.media_height = data.get("media_height") or 1080
        self.media_width = data.get("media_width") or 1920
        for key, value in data[kwargs.get("file_extensions") or "file_extensions"].items():
            setattr(save_extensions, key, value)
        self.options = data["options"]
        self._block_list = [Block(**caption) for caption in data["block_list"]]

    def fromLegacyJson(self, file: str, **kwargs):
        encoding = kwargs.get("encoding") or "UTF-8"
        if encoding == "auto":
            encoding = self.getEncoding(file)
        _, ext = os.path.splitext(file)
        if not ext:
            file += ".json"
        try:
            with open(file, "r", encoding=encoding) as f:
                data = json.load(f)
            self._loadJson(data, file_extensions="extensions")
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
        except Exception as e:
            print(f"Error {e}")

    def fromJson(self, file: str, **kwargs):
        encoding = kwargs.get("encoding") or "UTF-8"
        if encoding == "auto":
            encoding = self.getEncoding(file)
        _, ext = os.path.splitext(file)
        if not ext:
            file += ".json"
        try:
            with open(file, "r", encoding=encoding) as f:
                data = json.load(f)
                if not data.get("identifier") or not data["identifier"] == "pycaptions":
                    raise ValueError("Incorect json format: File data does not contain 'identifier' with value of 'pycaptions'" +
                                     "\nIf you have saves before 0.5.1 run your arguments with 'fromLegacyJson' function.")
                compatibility = dict()
                version = data.get("json_version")
                if not version == JSON_VERSION:
                    pass
                self._loadJson(data, **compatibility)
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
        except Exception as e:
            print(f"Error {e}")

    def toJson(self, file: str, **kwargs):
        encoding = kwargs.get("encoding") or "UTF-8"

        def serializer(obj):
            if hasattr(obj, '__json__'):
                return obj.__json__()
            else:
                return vars(obj)
        try:
            filename = ""
            if self.isFile:
                filename = self.file_name_or_content

            data = {
                    "identifier": "pycaptions",
                    "json_version": self.json_version,
                    "default_language": self.default_language,
                    "time_length": self.time_length,
                    "filename": filename,
                    "media_height": self.media_height,
                    "media_width": self.media_width,
                    "file_extensions": vars(self.extensions),
                    "options": self.options,
                    "block_list": self._block_list
                           }
            if kwargs.get("save_as"):
                if kwargs.get("save_as") == "string":
                    return json.dumps(data, default=serializer)
                elif kwargs.get("save_as") == "dict":
                    return copy.deepcopy(data)
                elif kwargs.get("save_as") == "caption_array":
                    return [{"start": i.start_time, "end": i.end_time, "text": i.get()}
                            for i in self if i.block_type == BlockType.CAPTION]
                else:
                    raise ValueError(f"Invalid save_as value, got {kwargs.get('save_as')}" +
                                     ", expected string, dict, caption_array")
            else:
                if not file.endswith(".json"):
                    file += ".json"
                with open(file, "w", encoding=encoding) as f:
                    json.dump(data, f, default=serializer)
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")
        except Exception as e:
            print(f"Error {e}")

    def join(self, captionsFormat, add_end_time: bool = False, time: MT = None, **kwargs):
        """
        Join two CaptionsFormat instances by appending blocks from the provided format to the current format.

        Args:
            captionsFormat (CaptionsFormat): The CaptionsFormat instance to join with.
            add_end_time (bool, optional): If True, current end time is added to the time offset.
            microseconds (int, optional): Time offset by microseconds.
            miliseconds (int, optional): Time offset by milliseconds.
            seconds (int, optional): Time offset by seconds.
            minutes (int, optional): Time offset by minutes.
            hours (int, optional): Time offset by hours.
            **kwargs: Additional options for customization (e.g. file encoding).
        """
        if not isinstance(captionsFormat, CaptionsFormat):
            raise ValueError("Unsupported type. Must be an instance of `CaptionsFormat`")

        time_offset = time or MT()
        if add_end_time:
            time_offset += self.time_length

        for caption in captionsFormat:
            self.append(caption.copy())
            self[-1].shift_end_us(time_offset)

    def joinFile(self, filename: str, add_end_time: bool = False, time: MT = None, **kwargs):
        """
        Join captions from file by appending blocks to the current format.

        Args:
            captionsFormat (CaptionsFormat): The CaptionsFormat instance to join with.
            add_end_time (bool, optional): If True, current end time is added to the time offset.
            microseconds (int, optional): Time offset by microseconds.
            miliseconds (int, optional): Time offset by milliseconds.
            seconds (int, optional): Time offset by seconds.
            minutes (int, optional): Time offset by minutes.
            hours (int, optional): Time offset by hours.
            **kwargs: Additional options for customization (e.g. file encoding).
        """
        encoding = kwargs.get("encoding") or "UTF-8"

        time_offset = time or MT()
        if add_end_time:
            time_offset += self.time_length

        with open(filename, "r", encoding=encoding) as stream:
            if self.detect(stream):
                self.read(stream, self.getLanguagesFromFilename(filename), time_offset=time_offset)

    def getEncoding(self, file: str):
        with open(file, "rb") as f:
            return detect_encoding(f.read()).get("encoding")
