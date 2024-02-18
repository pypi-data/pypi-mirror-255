import numpy as np
import pytest

from mfire.composite import ComparisonOperator
from mfire.text.comment import FFRafBuilder, RepresentativeValueBuilder
from mfire.text.comment.representative_builder import (
    AltitudeBuilder,
    FFBuilder,
    PrecipBuilder,
    RepresentativeValueClass,
    RepresentativeValueManager,
    SnowBuilder,
    TemperatureBuilder,
)
from tests.text.comment.factories import ComponentInterfaceFactory


dict_in_dataset = [
    # nothing
    {},
    # plain with no value
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": None,
            "next_critical": None,
            "threshold": None,
        }
    },
    # mountain with no value
    {
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": None,
            "next_critical": None,
            "threshold": None,
        }
    },
    # plain case
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        }
    },
    # local plain cases
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 10.0,
            "threshold": 5.0,
        }
    },
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": 15.0,
            "threshold": 12.0,
            "occurrence_event": True,
        }
    },
    # plain case when plain case rep = local case rep
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 12.0,
            "threshold": 5.0,
        }
    },
    # mountain case
    {
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        }
    },
    # local mountain cases
    {
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 10.0,
            "threshold": 5.0,
        }
    },
    {
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 5.0,
            "next_critical": 10.0,
            "threshold": 12.0,
            "occurrence_event": True,
        }
    },
    # mountain case when mountain case rep = local mountain case rep
    {
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 12.0,
            "threshold": 5.0,
        }
    },
    # plain and mountain cases when plain rep = mountain rep
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": None,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": None,
            "threshold": 5.0,
        },
    },
    # plain and mountain cases when plain rep < mountain rep
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 7.0,
            "next_critical": None,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": None,
            "threshold": 5.0,
        },
    },
    # local plain and mountain cases
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 10.0,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        },
    },
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 5.0,
            "next_critical": 10.0,
            "threshold": 12.0,
            "occurrence_event": True,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        },
    },
    # plain and local mountain case
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 10.0,
            "threshold": 5.0,
        },
    },
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 10.0,
            "next_critical": None,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 5.0,
            "next_critical": 10.0,
            "threshold": 12.0,
            "occurrence_event": True,
        },
    },
    # local plain and local mountain case
    {
        "plain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 12.0,
            "next_critical": 10.0,
            "threshold": 5.0,
        },
        "mountain": {
            "units": "cm",
            "operator": ComparisonOperator.SUPEGAL,
            "value": 5.0,
            "next_critical": 13.0,
            "threshold": 15.0,
            "occurrence_event": True,
        },
    },
]


class TestRepresentativeValueClass:
    @pytest.mark.parametrize(
        "prefix,expected_class",
        [
            ("FF", FFBuilder),
            ("RAF", FFRafBuilder),
            ("T", TemperatureBuilder),
            ("PRECIP", PrecipBuilder),
            ("EAU", PrecipBuilder),
            ("NEIPOT", SnowBuilder),
            ("*", None),
        ],
    )
    def test_get_builder_by_prefix(self, prefix, expected_class):
        result = RepresentativeValueClass.get_builder_by_prefix(prefix)
        if expected_class is not None:
            assert isinstance(result, expected_class)
        else:
            assert result is None


class TestRepresentativeValueManager:
    @pytest.mark.parametrize(
        "params,expected",
        [
            (["NEIPOT1", "NEIPOT6", "NEIPOT24"], True),
            (["NEIPOT1__SOL", "NEIPOT6__SOL", "NEIPOT24__SOL"], True),
            (["NEIPOT1", "PRECIP12", "EAU1"], True),
            (["NEIPOT1__SOL", "PRECIP12__SOL", "EAU1__SOL"], True),
            (["FF__HAUTEUR", "RAF__HAUTEUR"], True),
            (["NEIPOT1", "FF__HAUTEUR"], False),
            (["NEIPOT1__SOL", "FF__HAUTEUR"], False),
            (["XXX__HAUTEUR"], False),  # since XXX isn't a family
        ],
    )
    def test_are_values_homogenous(self, params, expected):
        manager = RepresentativeValueManager()
        dict_params = {p: None for p in params}
        assert manager.are_values_homogenous(dict_params) == expected

    @pytest.mark.parametrize(
        "reduction",
        [
            # only plain
            {
                "NEIPOT1__SOL": {
                    "plain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 2,
                        "threshold": 1,
                    },
                },
            },
            # only mountain
            {
                "NEIPOT1__SOL": {
                    "mountain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 2,
                        "threshold": 1,
                    },
                },
            },
            # plain and mountain
            {
                "NEIPOT1__SOL": {
                    "plain": {
                        "units": "mm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 30,
                        "threshold": 15,
                    },
                    "mountain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 2,
                        "threshold": 1,
                    },
                },
            },
            # rep value > next_critical
            {
                "NEIPOT1__SOL": {
                    "plain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 3,
                        "threshold": 1,
                        "next_critical": 2,
                    },
                },
            },
            # rep value < threshold
            {
                "NEIPOT1__SOL": {
                    "plain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 1,
                        "threshold": 3,
                    },
                },
            },
            # not homogeneous
            {
                "NEIPOT1__SOL": {},
                "RAF__HAUTEUR10": {},
            },
            # homogeneous
            {
                "NEIPOT1__SOL": {
                    "plain": {
                        "units": "mm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 30,
                        "threshold": 15,
                    }
                },
                "NEIPOT24__SOL": {
                    "plain": {
                        "units": "cm",
                        "operator": ComparisonOperator.SUPEGAL,
                        "value": 4,
                        "threshold": 3,
                    },
                },
            },
        ],
    )
    def test_process_rep_value_and_get_rep_value(self, reduction, assert_equals_result):
        """
        This function tests both methods process_rep_value and get_rep_value
        """

        # monozone case
        np.random.seed(1)
        manager = RepresentativeValueManager()
        manager.process_rep_value(reduction)
        assert_equals_result(manager._text)

        # mulitzone case
        np.random.seed(1)
        manager = RepresentativeValueManager()
        manager.component_handler = ComponentInterfaceFactory()
        manager.component_handler.critical_value = reduction
        manager.process_rep_value(None)
        assert_equals_result(manager._text)


class TestRepresentativeValueBuilder:
    @pytest.mark.parametrize(
        "var_name,expected",
        [
            ("NEIPOT1__SOL", "1 heure"),
            ("NEIPOT6__SOL", "6 heures"),
            ("EAU1__SOL", "1 heure"),
            ("FF__HAUTEUR", ""),
        ],
    )
    def test_accumulated_hours(self, var_name, expected):
        assert RepresentativeValueBuilder.accumulated_hours(var_name) == expected

    @pytest.mark.parametrize("unit,expected", [("cm", "cm"), (None, "")])
    def test_units(self, unit, expected):
        assert RepresentativeValueBuilder.units(unit) == expected

    def test_around(self):
        np.random.seed(1)
        assert RepresentativeValueBuilder().around == "aux alentours de"

    @pytest.mark.parametrize(
        "x,expected",
        [(None, None), (1e-7, None), (1e-5, "1e-05"), (10, "10"), (100.258, "100.258")],
    )
    def test_round(self, x, expected):
        assert RepresentativeValueBuilder.round(x) == expected

    def test_template(self):
        np.random.seed(0)
        builder = RepresentativeValueBuilder()
        assert (
            builder.template("XXX") == "Echec dans la récupération du template ("
            "key=XXX) (error COM-001)."
        )
        assert (
            builder.template("plain")
            == "On prévoit {indefinite_var_name} {around} {value}."
        )

    @pytest.mark.parametrize(
        "dict_in,expected",
        [  # no operator
            (
                {
                    "operator": None,
                    "next_critical": 12,
                    "value": 10,
                },
                (None, None),
            ),
            # no value
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "threshold": 10,
                    "value": None,
                },
                (None, None),
            ),
            # no next_critical
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": None,
                    "threshold": 10,
                    "value": 10,
                },
                (10, None),
            ),
            # value < next_critical
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "threshold": 10,
                    "value": 10,
                },
                (10, None),
            ),
            # value > next_critical
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "value": 15,
                    "threshold": 10,
                },
                (11, 15),
            ),
            # value < threshold with occurrence
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 15,
                    "value": 10,
                    "threshold": 12,
                    "occurrence_event": True,
                },
                (10, 12),
            ),
            # value < threshold without occurrence
            (
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 15,
                    "value": 10,
                    "threshold": 12,
                    "occurrence_event": False,
                },
                (10, None),
            ),
        ],
    )
    def test_replace_critical(self, dict_in, expected):
        assert RepresentativeValueBuilder.replace_critical(dict_in) == expected

    @pytest.mark.parametrize("dict_in", dict_in_dataset)
    def test_get_sentence_and_format_table(self, dict_in, assert_equals_result):
        np.random.seed(1)
        builder = RepresentativeValueBuilder()
        builder.phenomenon = "phen"
        builder.def_article = "def"
        builder.indef_article = "indef"
        assert_equals_result(
            builder.get_sentence_and_format_table("FF__HAUTEUR", dict_in)
        )

    @pytest.mark.parametrize("dict_in", dict_in_dataset)
    def test_format(self, dict_in, assert_equals_result):
        np.random.seed(1)
        builder = RepresentativeValueBuilder()
        builder.phenomenon = "phen"
        builder.def_article = "def"
        builder.indef_article = "indef"
        assert_equals_result(builder.format("FF__HAUTEUR", dict_in))

    @pytest.mark.parametrize(
        "var_name,dict_in,only_values,expected",
        [
            (
                "EAU24__SOL",
                {"operator": None, "next_critical": 12, "value": 10, "threshold": 5},
                True,
                None,
            ),  # no operator
            (
                "EAU24__SOL",
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "value": None,
                    "threshold": 5,
                },
                True,
                None,
            ),  # no value
            (
                "EAU24__SOL",
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "value": 10,
                    "units": "cm",
                    "threshold": 5,
                },
                True,
                "10 cm en 24 h",
            ),  # value < next_critical and only values
            (
                "EAU24__SOL",
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 12,
                    "value": 10,
                    "units": "cm",
                    "threshold": 5,
                },
                False,
                "indef phen de 10 cm en 24 h",
            ),  # value < next_critical and not only values
            (
                "EAU1__SOL",
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 10,
                    "value": 12,
                    "units": "cm",
                    "threshold": 5,
                },
                True,
                "9 cm (localement 12 cm) en 1 h",
            ),  # value > next_critical and only values
            (
                "EAU1__SOL",
                {
                    "operator": ComparisonOperator.SUP,
                    "next_critical": 10,
                    "value": 12,
                    "units": "cm",
                    "threshold": 5,
                },
                False,
                "indef phen de 9 cm (localement 12 cm) en 1 h",
            ),  # value > next_critical and not only values
        ],
    )
    def test_short_description(self, var_name, dict_in, only_values, expected):
        np.random.seed(1)
        builder = RepresentativeValueBuilder()
        builder.phenomenon = "phen"
        builder.def_article = "def"
        builder.indef_article = "indef"
        assert builder.short_description(var_name, dict_in, only_values) == expected


class TestFFBuilder:
    def test_definite_var_name(self):
        assert FFBuilder().definite_var_name("FF__HAUTEUR") == "le vent moyen"

    def test_indefinite_var_name(self):
        assert FFBuilder().indefinite_var_name("FF__HAUTEUR") == "un vent moyen"

    @pytest.mark.parametrize(
        "x,expected",
        [
            (None, None),
            (1e-7, None),
            (1e-5, "0 à 5"),
            (7.5, "5 à 10"),
            (12.5, "10 à 15"),
        ],
    )
    def test_round(self, x, expected):
        assert FFBuilder.round(x) == expected


class TestTemperatureBuilder:
    def test_definite_var_name(self):
        assert TemperatureBuilder().definite_var_name("FF__HAUTEUR") == "la température"

    def test_indefinite_var_name(self):
        assert (
            TemperatureBuilder().indefinite_var_name("FF__HAUTEUR") == "une température"
        )

    @pytest.mark.parametrize(
        "x,operator,expected",
        [
            (None, "<", None),
            (None, ">", None),
            (1e-7, "<", "0"),
            (1e-7, ">", "1"),
            (7.5, "<", "7"),
            (7.5, ">", "8"),
        ],
    )
    def test_round(self, x, operator, expected):
        assert TemperatureBuilder.round(x, operator) == expected


class TestFFRafBuilder:
    def test_definite_var_name(self):
        assert FFRafBuilder().definite_var_name("FF__HAUTEUR") == "les rafales"

    def test_indefinite_var_name(self):
        assert FFRafBuilder().indefinite_var_name("FF__HAUTEUR") == "des rafales"

    @pytest.mark.parametrize(
        "x,around,expected",
        [
            (None, None, None),
            (1e-7, None, None),
            (1e-5, None, "0 à 10"),
            (7.5, None, "0 à 10"),
            (7.5, "comprises entre", "0 et 10"),
        ],
    )
    def test_round(self, x, around, expected):
        assert FFRafBuilder.round(x, around=around) == expected


class TestSnowBuilder:
    def test_definite_var_name(self):
        assert (
            SnowBuilder().definite_var_name("FF__HAUTEUR") == "le potentiel de "
            "neige sur "
        )

    def test_indefinite_var_name(self):
        assert (
            SnowBuilder().indefinite_var_name("FF__HAUTEUR") == "un potentiel de "
            "neige sur "
        )

    @pytest.mark.parametrize(
        "x,expected",
        [
            (None, None),
            (1e-7, None),
            (1e-5, "0 à 1"),
            (1.5, "1 à 3"),
            (4.5, "3 à 5"),
            (6.5, "5 à 7"),
            (7.5, "7 à 10"),
            (12.5, "10 à 15"),
            (17.5, "15 à 20"),
            (25, "20 à 30"),
            (115, "110 à 120"),
        ],
    )
    def test_round(self, x, expected):
        assert SnowBuilder.round(x) == expected


class TestPrecipBuilder:
    def test_definite_var_name(self):
        assert (
            PrecipBuilder().definite_var_name("PRECIP3__SOL")
            == "le cumul de précipitation sur 3 heures"
        )
        assert (
            PrecipBuilder().definite_var_name("EAU1__SOL")
            == "le cumul de pluie sur 1 heure"
        )
        assert PrecipBuilder().definite_var_name("FF__HAUTEUR") == ""

    def test_indefinite_var_name(self):
        assert (
            PrecipBuilder().indefinite_var_name("PRECIP3__SOL")
            == "un cumul de précipitation sur 3 heures"
        )
        assert (
            PrecipBuilder().indefinite_var_name("EAU1__SOL")
            == "un cumul de pluie sur 1 heure"
        )
        assert PrecipBuilder().indefinite_var_name("FF__HAUTEUR") == ""

    @pytest.mark.parametrize(
        "x,expected",
        [
            (None, None),
            (1e-7, None),
            (1e-5, "au maximum 3"),
            (1.5, "au maximum 3"),
            (4.5, "3 à 7"),
            (7.5, "7 à 10"),
            (12.5, "10 à 15"),
            (17.5, "15 à 20"),
            (22, "20 à 25"),
            (27, "25 à 30"),
            (35, "30 à 40"),
            (45, "40 à 50"),
            (55, "50 à 60"),
            (70, "60 à 80"),
            (90, "80 à 100"),
            (115, "100 à 150"),
            (1215, "1200 à 1250"),
        ],
    )
    def test_round(self, x, expected):
        assert PrecipBuilder.round(x) == expected

    def test_format(self, assert_equals_result):
        # This test handles the conversion au "au" to "d'"
        np.random.seed(1)  # in order to have a sentence with around word
        dict_in = {
            "plain": {
                "units": "cm",
                "operator": ComparisonOperator.SUPEGAL,
                "value": 1.5,
                "next_critical": None,
                "threshold": 1,
            }
        }
        assert_equals_result(PrecipBuilder().format("PRECIP24__SOL", dict_in))


class TestAltitudeBuilder:
    def test_definite_var_name(self):
        assert (
            AltitudeBuilder().definite_var_name("FF__HAUTEUR")
            == "le potentiel de neige sur "
        )

    def test_indefinite_var_name(self):
        assert (
            AltitudeBuilder().indefinite_var_name("FF__HAUTEUR")
            == "un potentiel de neige sur "
        )

    @pytest.mark.parametrize("dict_in", dict_in_dataset)
    def test_get_sentence_and_format_table(self, dict_in, assert_equals_result):
        np.random.seed(1)
        assert_equals_result(
            AltitudeBuilder().get_sentence_and_format_table(
                "_", {"NEIPOT24__SOL": dict_in}
            )
        )

    @pytest.mark.parametrize("dict_in", dict_in_dataset)
    def test_format(self, dict_in, assert_equals_result):
        np.random.seed(1)
        assert_equals_result(AltitudeBuilder().format("_", {"NEIPOT1__SOL": dict_in}))
