import budoux

def get_phrases(text, lang):
    if lang == "ja":
        parser = budoux.load_default_japanese_parser()
        return parser.parse(text)
    if lang in ["zh", "zh-CN", "zh-SG", "zh-Hans"]:
        parser = budoux.load_default_simplified_chinese_parser()
        return parser.parse(text)
    if lang in ["zh-HK", "zh-MO", "zh-TW", "zh-Hant"]:
        parser = budoux.load_default_simplified_chinese_parser()
        return parser.parse(text)
    if lang == "th":
        parser = budoux.load_default_thai_parser()
        return parser.parse(text)
    
    return text.split(" ")

def get_lines_ratio(lines, total_characters, character_limit, split_ratios, smaller_first_line):
    if lines > 0:
        if smaller_first_line:
            pass
        target_characters = total_characters - lines + 1
        current_limit = sum(character_limit * ratio for ratio in split_ratios)
        if current_limit < target_characters:
            remaining = (target_characters - current_limit) / total_characters
            for index, _ in enumerate(split_ratios):
                split_ratios[index] += remaining

    return split_ratios