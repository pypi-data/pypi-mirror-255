from mfire.utils.string_utils import letter_is_vowel


def prefix_by_de_or_d(input_str: str):
    if letter_is_vowel(input_str[0], True):
        return f"d'{input_str}"
    return f"de {input_str}"
