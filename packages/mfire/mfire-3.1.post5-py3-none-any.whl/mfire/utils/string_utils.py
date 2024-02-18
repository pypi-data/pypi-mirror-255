from __future__ import annotations

import re
import unicodedata
from typing import List, Optional, Tuple, Union

from mfire.settings import TEMPLATES_FILENAMES, Settings
from mfire.utils import JsonFile
from mfire.utils.date import Datetime

SYNONYMS = JsonFile(TEMPLATES_FILENAMES[Settings().language]["synonyms"]).load()


def get_synonym(word: str) -> str:
    """
    Returns a random synonym of the given word.

    Args:
        word (str): The word for which a synonym is desired.

    Returns:
        str: A random synonym of the given word.
    """
    iter_synonyms = next((seq for seq in SYNONYMS if word in seq), (word,))
    return Settings().random_choice(iter_synonyms)


def match_text(text1: str, text2: str, synonyms: Optional[Tuple] = None) -> bool:
    """
    Checks if a text matches a given template by comparing them after replacing
    synonyms.

    Args:
        text1 (str): The text to compare with the template.
        text2 (str): The template with tags between '<...>'.
        synonyms (Optional[Tuple]): Mapping between tags and possible values. Defaults
        to None.

    Returns:
        bool: True if the text matches the template, False otherwise.
    """
    if synonyms is None:
        synonyms = SYNONYMS
    ntext1, ntext2 = text1, text2
    for seq in synonyms:
        tag = f"<{seq[0]}>"
        for word in seq:
            ntext1 = ntext1.replace(word, tag)
            ntext2 = ntext2.replace(word, tag)
    return ntext1 == ntext2


def decapitalize(string: str) -> str:
    """
    Decapitalizes only the first letter of a string.

    Args:
        string (str): The input string.

    Returns:
        str: The decapitalized string.
    """
    return string[:1].lower() + string[1:]


def capitalize(string: str) -> str:
    """
    Capitalizes only the first letter of a string.

    Args:
        string (str): The input string.

    Returns:
        str: The capitalized string.
    """
    return string[:1].upper() + string[1:]


def capitalize_all(string: str) -> str:
    """
    Capitalizes all sentences in a string.

    Args:
        string (str): The input string.

    Returns:
        str: The string with all sentences capitalized.
    """
    f = filter(None, string.split("."))
    all_strings = [capitalize(s.strip()) for s in f]

    return concatenate_string(
        all_strings, delimiter=". ", last_delimiter=". ", last_ponctuation="."
    )


def concatenate_string(
    iterator: Union[List[str], iter],
    delimiter: str = ", ",
    last_delimiter: str = " et ",
    last_ponctuation: str = "",
) -> str:
    """
    Concatenates a list of strings with specified delimiters.

    Args:
        iterator (Union[List[str], iter]): The list or iterator of strings to
        concatenate.
        delimiter (str, optional): The delimiter between strings. Defaults to ", ".
        last_delimiter (str, optional): The delimiter before the last string. Defaults
            to " et ".
        last_ponctuation (str, optional): The punctuation to add at the end. Defaults
            to "".

    Returns:
        str: The concatenated string.
    """
    list_it = list(iterator)
    if list_it == []:
        return ""

    return (
        delimiter.join(list_it[:-1]) + last_delimiter + list_it[-1]
        if len(list_it) > 1
        else f"{list_it[0]}"
    ) + last_ponctuation


def clean_french_text(text: str) -> str:
    """
    Cleans up French text by replacing certain patterns.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.
    """
    text = text.strip()
    text = re.sub(r"[  ](celsius|°C)", "°C", text)

    text = re.sub(r"jusqu.à au", "jusqu'au", text)
    text = re.sub(r"jusqu.à le", "jusqu'au", text)
    text = re.sub(r"jusqu.à en", "jusqu'en", text)
    text = re.sub(r"([^\w_])dès en début", r"\1dès le début", text)
    text = re.sub(r"([^\w_])dès en première", r"\1dès la première", text)
    text = re.sub(r"([^\w_])dès en fin", r"\1dès la fin", text)
    text = re.sub(r"([^\w_])que en", r"\1qu'en", text)
    text = re.sub(r"([^\w_])de en ce", r"\1du", text)
    text = re.sub(r"([^\w_])de en début", r"\1du début", text)
    text = re.sub(r"([^\w_])de en milieu", r"\1du milieu", text)
    text = re.sub(r"([^\w_])de en fin", r"\1de la fin", text)
    text = re.sub(r"([^\w_])de en première", r"\1de la première", text)
    text = re.sub(r"([^\w_])de ([aeiouy])", r"\1d'\2", text)

    text = re.sub(r"\.[ ]*\.", ".", text)  # Replaces ".." or ".   ." with "."
    text = re.sub(r"\,[ ]*\.", ".", text)  # Replaces ",." or ",   ." with "."
    text = re.sub("[ ]+ ", " ", text)
    text = re.sub("[ ]+", " ", text)

    return capitalize_all(text)


def split_accumulation_var_name(
    var_name: str,
) -> Tuple[str, Optional[int], Optional[str]]:
    """
    Splits a variable name following the pattern <prefix><accum>__<vertical_level>
    into a tuple (<prefix>, <accum>, <vertical_level>).

    Args:
        var_name (str): The variable name.

    Returns:
        Tuple[str, Optional[int], Optional[str]]: A tuple containing:
            - The prefix
            - The accumulation value (optional)
            - The vertical level (optional)
    """
    prefix, accum, vert_level = re.match(
        r"^([a-zA-Z_]+)(\d*)__(.*)$", var_name
    ).groups()

    if accum == "":
        accum = 0

    return prefix, int(accum), vert_level


class TagFormatter:
    """
    TagFormatter: Format a string containing tags of the form '[key:func]'.
    It follows the Vortex standard.
    """

    time_format: dict = {
        "fmth": "{:04d}",
        "fmthm": "{:04d}:00",
        "fmthhmm": "{:02d}:00",
        "fmtraw": "{:04d}00",
    }
    datetime_format: dict = {
        "julian": "%j",
        "ymd": "%Y%m%d",
        "yymd": "%y%m%d",
        "y": "%Y",
        "ymdh": "%Y%m%d%H",
        "yymdh": "%y%m%d%H",
        "ymdhm": "%Y%m%d%H%M",
        "ymdhms": "%Y%m%d%H%M%S",
        "mmddhh": "%m%d%H",
        "mm": "%m",
        "hm": "%H%M",
        "dd": "%d",
        "hh": "%H",
        "h": "%-H",
        "vortex": "%Y%m%dT%H%M%S",
        "stdvortex": "%Y%m%dT%H%M",
        "iso8601": "%Y-%m-%dT%H:%M:%SZ",
    }

    def format_tags(self, text: str, tags: dict = None) -> str:
        """
        Formats a string containing tags of the form '[key:func]'.

        Args:
            text (str): The text to format.
            tags (dict, optional): A dictionary of tag-value pairs. Defaults to None.

        Returns:
            str: The formatted string.
        """
        if not tags:
            return text

        for key, value in tags.items():
            # Raw key formatting
            text = text.replace("[{}]".format(key), str(value))

            # Time formatting
            if isinstance(value, int):
                for func, fmt in self.time_format.items():
                    text = text.replace("[{}:{}]".format(key, func), fmt.format(value))
            # Datetime formatting
            try:
                value_dt = Datetime(value)
                for func, fmt in self.datetime_format.items():
                    text = text.replace(
                        "[{}:{}]".format(key, func), value_dt.strftime(fmt)
                    )
            except (TypeError, ValueError):
                pass

            # Geometry formatting
            text = text.replace("[{}:area]".format(key), str(value).upper())

        return text


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii.decode("utf-8")


def letter_is_vowel(letter: str, handle_accents: bool) -> bool:
    if handle_accents is True:
        letter: str = remove_accents(letter)
    return letter.lower() in ["a", "e", "i", "o", "u", "y"]
