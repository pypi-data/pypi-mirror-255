import numpy as np
import pytest

from mfire.utils.string_utils import (
    TagFormatter,
    capitalize,
    capitalize_all,
    clean_french_text,
    concatenate_string,
    decapitalize,
    get_synonym,
    match_text,
    split_accumulation_var_name,
)


class TestStringUtilsFunctions:
    def test_get_synonym(self):
        np.random.seed(42)
        assert get_synonym("à environ") == "de l'ordre de"
        assert get_synonym("fort") == "marqué"
        assert get_synonym("abc") == "abc"

    @pytest.mark.parametrize(
        "text1,text2,expected",
        [
            ("Les vents seront forts", "Les vents seront marqués", True),
            ("Les vents seront faibles", "Les vents seront marqués", False),
        ],
    )
    def test_match_text(self, text1, text2, expected):
        assert match_text(text1, text2) == expected

    def test_decapitalize(self):
        assert (
            decapitalize("Première phrase. Deuxième phrase.")
            == "première phrase. Deuxième phrase."
        )

    def test_capitalize(self):
        assert (
            capitalize("première phrase. deuxième phrase.") == "Première phrase. "
            "deuxième phrase."
        )

    @pytest.mark.parametrize(
        "string,expected",
        [
            (
                ("phrase 1."),
                ("Phrase 1."),
            ),
            (
                ("phrase 1. phrase 2.       Phrase 3."),
                ("Phrase 1. Phrase 2. Phrase 3."),
            ),
        ],
    )
    def test_capitalize_all(self, string, expected):
        assert capitalize_all(string) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            # Basic correction
            ("text1  text2", "Text1 text2."),
            ("lundi orages   ; puis averses", "Lundi orages ; puis averses."),
            # Syntaxic correction
            ("jusqu'à au jeudi", "Jusqu'au jeudi."),
            ("jusqu'à le jeudi", "Jusqu'au jeudi."),
            ("jusqu'à en début de soirée", "Jusqu'en début de soirée."),
            ("alerte dès en début de journée", "Alerte dès le début de journée."),
            (
                "alerte dès en première partie de journée",
                "Alerte dès la première partie de journée.",
            ),
            ("alerte dès en fin de nuit", "Alerte dès la fin de nuit."),
            ("alerte que en début de nuit", "Alerte qu'en début de nuit."),
            (
                "rafales à partir de en ce milieu de nuit.",
                "Rafales à partir du milieu de nuit.",
            ),
            (
                "rafales à partir de en début de nuit.",
                "Rafales à partir du début de nuit.",
            ),
            (
                "rafales à partir de en milieu de cette nuit",
                "Rafales à partir du milieu de cette nuit.",
            ),
            (
                "rafales à partir de en fin de nuit",
                "Rafales à partir de la fin de nuit.",
            ),
            (
                "rafales à partir de en première partie de la nuit",
                "Rafales à partir de la première partie de la nuit.",
            ),
            ("rafales à partir de aujourd'hui", "Rafales à partir d'aujourd'hui."),
            # Ponctuation corrections
            ("rafales..", "Rafales."),
            ("rafales.    .", "Rafales."),
            ("rafales,.", "Rafales."),
            ("rafales,     .", "Rafales."),
            # Celsius corrections
            ("températures à 33 °C", "Températures à 33°C."),
            ("températures à 33 °C", "Températures à 33°C."),
            ("températures à 33 celsius", "Températures à 33°C."),
            ("températures à 33 celsius", "Températures à 33°C."),
        ],
    )
    def test_clean_french_text(self, text, expected):
        assert clean_french_text(text) == expected

    def test_concatenate_string(self):
        assert concatenate_string([]) == ""
        assert concatenate_string(["test1"]) == "test1"
        assert concatenate_string(["test1"], last_ponctuation=".") == "test1."
        assert (
            concatenate_string(["test1", "test2", "test3"]) == "test1, test2 et "
            "test3"
        )

    @pytest.mark.parametrize(
        "var_name,expected",
        [
            ("EAU24__SOL", ("EAU", 24, "SOL")),
            ("FF__HAUTEUR", ("FF", 0, "HAUTEUR")),
        ],
    )
    def test_split_accumulation_var_name(self, var_name, expected):
        assert split_accumulation_var_name(var_name) == expected


class TestTagFormatter:
    @pytest.mark.parametrize(
        "text,tags,expected",
        [
            ("Datetime: [key:ymdhm]", {}, "Datetime: [key:ymdhm]"),
            ("Datetime: [key:ymd]", {"key": 1618617600}, "Datetime: 20210417"),
            (
                "Datetime: [key:ymdhm]",
                {"key": "20230301T0600"},
                "Datetime: 202303010600",
            ),
            (
                "Datetime: [key:vortex]",
                {"key": "20230301T0600"},
                "Datetime: 20230301T060000",
            ),
            # Error in the date
            (
                "Datetime: [key:ymdhm]",
                {"key": "20231301T0600"},
                "Datetime: [key:ymdhm]",
            ),
        ],
    )
    def test_format_tags(self, text, tags, expected):
        tag_formatter = TagFormatter()
        assert tag_formatter.format_tags(text, tags=tags) == expected
