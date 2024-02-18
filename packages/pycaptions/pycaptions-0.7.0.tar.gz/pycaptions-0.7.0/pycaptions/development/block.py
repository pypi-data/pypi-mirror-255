import copy

from collections import defaultdict
from langcodes import standardize_tag, tag_is_valid
from ..microTime import MicroTime as MT
from .styleFormat import cssParser
from ..styling import Styling
from .blockType import BlockType
from .text import get_phrases, get_lines_ratio


class Block:
    """
    Represents a block of content in a multimedia file or document.

    Methods:
        getLines: Format text of specific language into multiple lines
        get: Get the text content of the block for a specific language.
        append: Append text to the block for a specific language.
        shift_time: Shift start and end times of the block by a specified duration.
        shift_start: Shift start time of the block by a specified duration.
        shif_end: Shift end time of the block by a specified duration.
        copy: Returns a copy of the current block.
        shift_time_us: Shift time of the block by microseconds.
        shift_start_us: Shift start time of the block by microseconds.
        shift_end_us: Shift end time of the block by microseconds.
        __getitem__: Retrieve the text of specific language.
        __setitem__: Set the text of specific language.
        __str__: Return a string representation of the block.
        __iadd__: In-place addition for the Block.
        __add__: Addition for the Blocks.
        __isub__: In-place subtraction for a specific language.
        __sub__: Subtraction for a specific language.
        __iter__: Iterator for iterating through the block languages.
        __next__: Iterator method returning a tuple of language and text.
    """
    def __init__(self, block_type: int, default_language: str = "und", start_time: MT = None,
                 end_time: MT = None, text: str = "", **options):
        """
        Initialize a new instance of the Block class.

        Parameters:
        - block_type (int): The type of the block, represented as an integer, options in BlockType class
        - lang (str, optional): The language of the text in the block (default is "und" for undefined).
        - start_time (int, optional): The starting time of the block in microseconds (default is 0).
        - end_time (int, optional): The ending time of the block in microseconds (default is 0).
        - text (str, optional): The content of the block (default is an empty string).
        - **options: Additional keyword arguments for customization (e.g style, layout, ...).
        """
        self.block_type = block_type
        self.languages = defaultdict(str)
        if options.get("languages"):
            for i, j in options.get("languages").items():
                self.languages[i] = j
            del options["languages"]
        self.default_language = default_language
        if text:
            self.languages[default_language] = text.strip()
        self.start_time = start_time
        self.end_time = end_time
        if "options" in options:
            self.options = options["options"]
        else:
            self.options = options or {}

        if block_type == BlockType.STYLE and isinstance(self.options["style"], str):
            self.options["style"] = cssParser.parseString(cssText=self.options["style"], encoding="UTF-8")

    def __getitem__(self, index: str):
        return self.languages[index]

    def __setitem__(self, index: str, value: str):
        self.languages[index] = value

    def __delitem__(self, index: str):
        del self.languages[index]

    def __str__(self):
        temp = '\n'.join(f" {lang}: {text}" for lang, text in self.languages.items())
        return f"start: {self.start_time} end: {self.end_time}\n{temp}"

    def __iadd__(self, value):
        if not isinstance(value, Block):
            raise ValueError("Unsupported type. Must be an instance of `Block`")
        for key, language in value:
            self.languages[key] = language
        return self

    def __add__(self, value):
        if not isinstance(value, Block):
            raise ValueError("Unsupported type. Must be an instance of `Block`")
        out = self.copy()
        for key, language, comment in value:
            out.languages[key] = language
        return out

    def __isub__(self, language: str):
        if language in self.languages:
            del self.languages[language]
        return self

    def __sub__(self, language: str):
        out = self.copy()
        if language in out.languages:
            del out.languages[language]
        return out

    def __iter__(self):
        self._keys_iterator = iter(self.languages)
        return self

    def __next__(self):
        try:
            key = next(self._keys_iterator)
            return key, self.languages.get(key)
        except StopIteration:
            raise StopIteration

    def copy(self):
        return Block(self.block_type, self.default_language, self.start_time,
                     self.end_time, languages=copy.deepcopy(self.languages),
                     options=copy.deepcopy(self.options))

    def get(self, lang: str, lines: int = -1, **kwargs) -> str:
        return self.get_lines(lang, lines, **kwargs)

    def get_style(self, lang: str) -> str:
        return Styling(self.languages.get(lang), "html.parser")

    def get_lines(self, lang: str = None, lines: int = 0, character_limit: int = 47,
                  split_ratios: list[float] = [0.7, 1], smaller_first_line: bool = True, **kwargs) -> list[str]:
        """
        Format text of specific language into multiple lines.

        Args:
            lang (str, optional): Language code (default is None - uses default_language).
            lines (int, optional): The number of lines to format to. (default is 0 - autoformat). Ignores character limit and split ratios if it cannot fit in the desired amount.
            character_limit (int, optional) How many characters should be in a line. (default is 47)
            split_ratios (list[float], optional): Affects character_limit for n-th line. (default [0.7, 1])
            parser_language (str, optional): Parser language code, if None it uses lang.
        Returns:
            list[str]: A list of text lines.
        """

        lang = lang or self.default_language

        if lines == -1:
            return Styling(self.languages.get(lang), "html.parser").get_lines()

        separator = " "
        if "separator" in kwargs:
            separator = kwargs["separator"]

        text_lines = Styling(self.languages.get(lang), "html.parser").get_lines()
        text = next(text_lines)
        if text.endswith("-"):
            add_separator = False
        else:
            add_separator = True

        for i in text_lines:
            if add_separator:
                text += separator
            if i.endswith("-"):
                text += i[::-1]
                add_separator = False
            else:
                text += i
                add_separator = True

        length = len(text)

        if lines == 1:
            return [text]

        standardized = standardize_tag(kwargs.get("parser_language") or lang, macro=True)
        standardized = standardized if tag_is_valid(standardized) else "und"
        
        phrases = get_phrases(text, standardized)

        split_ratios = get_lines_ratio(lines, length, character_limit, split_ratios, smaller_first_line)

        formatted_lines = []
        current_line = []
        current_character_count = 0

        for index, phrase in enumerate(phrases):
            current_ratio_index = min(len(formatted_lines), len(split_ratios) - 1)
            effective_limit = int(character_limit * split_ratios[current_ratio_index])

            if current_character_count + len(phrase) <= effective_limit:
                current_line.append(phrase)
                current_character_count += len(phrase) + 1  # +1 for the space
            elif index+1 == len(phrases):
                current_line.append(phrase)
            else:
                formatted_lines.append(separator.join(current_line))
                current_line= [phrase]
                current_character_count = len(phrase) + 1

        if current_line:
            formatted_lines.append(separator.join(current_line))

        return formatted_lines

    def append(self, text: str, lang: str = None, separator: str = "<br>"):
        lang = lang or self.default_language
        if self.languages[lang]:
            self.languages[lang] += separator + text.strip()
        else:
            self.languages[lang] = text.strip()

    def append_without_common_part(self, text: str, lang: str = None):
        lang = lang or self.default_language
        common_lenght = 0
        current = self.get(lang)
        min_length = min(len(current), len(text))

        for i in range(min_length):
            if current[-i:] == text[:i]:
                common_lenght = i

        self.languages[lang] = current + text[common_lenght:]

    def shift_time_us(self, microseconds: int):
        self.start_time += microseconds
        self.end_time += microseconds

    def shift_time(self, time: MT):
        self.start_time += time
        self.end_time += time

    def shift_start_us(self, microseconds: int):
        self.start_time += microseconds

    def shift_start(self, time: MT):
        self.start_time += time

    def shift_end_us(self, microseconds: int):
        self.end_time += microseconds

    def shift_end(self, time: MT):
        self.end_time += time
