from collections.abc import Sequence
from typing import Any
from bs4.builder import TreeBuilder
from bs4.element import PageElement as PageElement, SoupStrainer as SoupStrainer
import cssutils

from bs4 import BeautifulSoup as BS
from cssutils import CSSParser
from cssutils.css import CSSStyleSheet as originalCSSStyleSheet

from .text import get_lines_ratio, get_phrases

class StyleSheet(originalCSSStyleSheet):
    def __json__(self):
        return str(self.cssText)


cssutils.css.CSSStyleSheet = StyleSheet

cssParser = CSSParser(validate=False)


class StyleFormat(BS):

    def __init__(self, markup="", features=None, builder=None,
                 parse_only=None, from_encoding=None, exclude_encodings=None,
                 element_classes=None, **kwargs):
        if "language" in kwargs:
            self.language = kwargs["language"]
            del kwargs["language"]
        else:
            self.language = "und"
        
        super().__init__(markup, features, builder, parse_only, from_encoding, exclude_encodings, element_classes, **kwargs)

    def parseStyle(self, string):
        return cssParser.parseStyle(string, encoding="UTF-8")
    
    def get_lines(self):
        return (BS(line.strip(), 'html.parser').get_text() for index, line in enumerate(str(self).split("<br/>")))

    def format_lines(self, lines: int = 0, character_limit: int = 47,
                     split_ratios: list[float] = [0.7, 1], smaller_first_line: bool = True, **kwargs) -> str:
        if lines == -1:
            return
        
        separator = " "
        if "separator" in kwargs:
            separator = kwargs["separator"]
        
        self.removeLineBreaks()
        if lines == 1:
            return

        length = sum(len(text_node) for text_node in self.find_all(string=True) if isinstance(text_node, str))
                
        split_ratios = get_lines_ratio(lines, length, character_limit, split_ratios, smaller_first_line)

        current_character_count = 0
        formated_lines = 0

        for text_node in self.find_all(string=True):
            if not isinstance(text_node, str):
                continue
            
            phrases = get_phrases(text_node, self.language)
            chunks = []
            current_line = []

            for index, phrase in enumerate(phrases):
                current_ratio_index = min(formated_lines, len(split_ratios) - 1)
                effective_limit = int(character_limit * split_ratios[current_ratio_index])
                if current_character_count + len(phrase) <= effective_limit:
                    current_line.append(phrase)
                    current_character_count += len(phrase) + 1
                elif index+1 == len(phrases):
                    current_line.append(phrase)
                else:
                    formated_lines += 1
                    chunks.append(separator.join(current_line))
                    current_line= [phrase]
                    current_character_count = len(phrase) + 1
            if current_line:
                chunks.append(separator.join(current_line))
            text_node.replace_with(BS('<br/>'.join(chunks), 'html.parser'))

    def removeLineBreaks(self):
        for br_tag in self.find_all('br'):
            previous_text = br_tag.find_previous(string=True)
            next_text = br_tag.find_next(string=True)
            if previous_text:
                if '-' in previous_text:
                    previous_text.replace_with(previous_text.replace('-', ''))
                    br_tag.replace_with('')
                else:
                    br_tag.replace_with(' ')
            else:
                br_tag.replace_with(' ')
            if next_text:
                next_text.replace_with(next_text.lstrip())