from configparser import ConfigParser
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mfire.text.template import (
    CentroidTemplateRetriever,
    CsvTemplateRetriever,
    IniTemplateRetriever,
    JsonTemplateRetriever,
    Template,
    TemplateRetriever,
    read_template,
)
from mfire.utils import JsonFile


def get_filename(dirname: Path, ext: str, opt: str = "") -> Path:
    """get_gilename : function which generate a name for a template file."""
    return Path(dirname) / f"{ext}_tpl{opt}.{ext}"


class TestTemplateFunctions:
    @pytest.mark.parametrize(
        "test_file", [{"extension": "json", "content": "{}"}], indirect=True
    )
    def test_read_template_with_json(self, test_file):
        assert isinstance(read_template(test_file.name), JsonTemplateRetriever)

    @pytest.mark.parametrize("test_file", [{"extension": "ini"}], indirect=True)
    def test_read_template_with_ini(self, test_file):
        assert isinstance(read_template(test_file.name), IniTemplateRetriever)

    @pytest.mark.parametrize(
        "test_file", [{"extension": "csv", "content": ","}], indirect=True
    )
    def test_read_template_with_csv(self, test_file):
        assert isinstance(read_template(test_file.name), CsvTemplateRetriever)

    @pytest.mark.parametrize(
        "test_file",
        [{"extension": "csv", "content": ",A,\nweights,1,"}],
        indirect=True,
    )
    def test_read_template_with_centroid(self, test_file):
        assert isinstance(read_template(test_file.name), CentroidTemplateRetriever)

    @pytest.mark.parametrize(
        "test_file", [{"extension": "csv", "content": ","}], indirect=True
    )
    def test_read_template_with_weights(self, test_file):
        weights = np.ndarray((1,), buffer=np.array([1]))
        assert isinstance(
            read_template(test_file.name, weights=weights), CentroidTemplateRetriever
        )

    @pytest.mark.parametrize(
        "test_file", [{"extension": "txt"}, {"extension": "yaml"}], indirect=True
    )
    def test_read_template_with_other_extensions(self, test_file):
        assert isinstance(read_template(test_file.name), TemplateRetriever)


class TestTemplate:
    def test_format(self):
        my_str = (
            "This is a {adj} template made by {template_author_name} in "
            "{template_date_year}!!"
        )
        my_tpl = Template(my_str)
        assert my_tpl.format() == my_str

        vars = {
            "template": {
                "author": {"name": "toto", "age": 30},
                "date": {"month": "may", "year": 2022},
            },
            "adj": "beautiful",
        }
        assert (
            my_tpl.format(**vars)
            == "This is a beautiful template made by toto in 2022!!"
        )


class TestTemplateRetriever:

    path = Path("test.json")
    content = {
        "A": "toto",
        "B": ["tata", "titi", "tutu"],
        "D": {"E": "tyty", "F": ["a", "b"]},
    }

    def test_init(self):
        tpl_rtr = TemplateRetriever(self.content)
        assert tpl_rtr.table == self.content
        assert tpl_rtr.get(("D", "F"), pop_method="first") == "a"

        assert tpl_rtr.get("A") == "toto"
        assert tpl_rtr.get("B") in ["tata", "titi", "tutu"]
        assert tpl_rtr.get("B", pop_method="first") == "tata"
        assert tpl_rtr.get("B", pop_method="last") == "tutu"

        pop_method = "-".join
        assert tpl_rtr.get("B", pop_method=pop_method) == "tata-titi-tutu"

        assert tpl_rtr.get("C", default="tete") == "tete"
        assert tpl_rtr.get("C") is None
        assert tpl_rtr.get(("D", "E")) == "tyty"

        assert tpl_rtr.get(("D", "F"), pop_method=lambda _: 1 / 0) is None
        assert (
            tpl_rtr.get(("D", "F"), pop_method=lambda _: 1 / 0, default="tete")
            == "tete"
        )

        assert (
            str(tpl_rtr) == "<class 'mfire.text.template.TemplateRetriever'>\n{'A': "
            "'toto', 'B': ['tata', 'titi', 'tutu'], 'D': {'E': 'tyty', 'F': ['a', "
            "'b']}}"
        )

    def test_read_file(self):
        assert TemplateRetriever.read_file(self.path) == TemplateRetriever(
            {"filename": self.path}
        )


class TestJsonTemplateRetriever:
    json_content = {
        "A": "toto",
        "B": ["tata", "titi", "tutu"],
        "D": {"E": "tyty", "F": ["a", "b"]},
    }

    def _check_get(self, tpl_rtr):
        assert isinstance(tpl_rtr, JsonTemplateRetriever)

        assert tpl_rtr.get("A") == "toto"
        assert tpl_rtr.get("B") in ["tata", "titi", "tutu"]
        assert tpl_rtr.get("B", pop_method="first") == "tata"
        assert tpl_rtr.get("B", pop_method="last") == "tutu"

        pop_method = "-".join
        assert tpl_rtr.get("B", pop_method=pop_method) == "tata-titi-tutu"

        assert tpl_rtr.get("C", default="tete") == "tete"
        assert tpl_rtr.get("C") is None
        assert tpl_rtr.get(("D", "E")) == "tyty"

        assert tpl_rtr.get(("D", "F"), pop_method="first") == "a"
        assert tpl_rtr.get(("D", "F"), pop_method=lambda _: 1 / 0) is None
        assert (
            tpl_rtr.get(("D", "F"), pop_method=lambda _: 1 / 0, default="tete")
            == "tete"
        )

    @pytest.mark.parametrize("test_file", [{"extension": "json"}], indirect=True)
    def test_init_and_read_file(self, test_file):
        tpl_rtr1 = JsonTemplateRetriever(self.json_content)
        self._check_get(tpl_rtr1)

        JsonFile(test_file.name).dump(self.json_content)
        tpl_rtr2 = read_template(test_file.name)
        assert tpl_rtr2 is not None
        self._check_get(tpl_rtr2)

        assert tpl_rtr1 == tpl_rtr2


class TestIniTemplateRetriever:
    @property
    def init_content(self):
        config = ConfigParser()
        config["DEFAULT"]["A"] = "toto"
        config["DEFAULT"]["B"] = "tata"
        config.add_section("D")
        config["D"]["E"] = "tyty"
        return config

    def _check_get(self, tpl_rtr):
        assert isinstance(tpl_rtr, IniTemplateRetriever)

        assert tpl_rtr.get("A") == "toto"
        assert tpl_rtr.get("B") == "tata"
        assert tpl_rtr.get("C", default="tete") == "tete"
        assert tpl_rtr.get("C") is None
        assert tpl_rtr.get(("D", "E")) == "tyty"

    @pytest.mark.parametrize("test_file_path", [{"extension": "ini"}], indirect=True)
    def test_init_and_read_file(self, test_file_path):
        tpl_rtr1 = IniTemplateRetriever(self.init_content)
        self._check_get(tpl_rtr1)

        f = open(test_file_path, "w")
        self.init_content.write(f)
        f.close()

        tpl_rtr2 = read_template(test_file_path)
        self._check_get(tpl_rtr2)

        assert tpl_rtr1 == tpl_rtr2


class TestCsvTemplateRetriever:

    csv_content = pd.DataFrame(
        [[0, 0, "toto"], [0, 1, "tata"], [1, 0, "titi"], [1, 1, "tutu"]],
        columns=["A", "B", "template"],
    ).set_index(["A", "B"])

    def _check_get(self, tpl_rtr):
        assert isinstance(tpl_rtr, CsvTemplateRetriever)

        assert tpl_rtr.get((0, 0)) == "toto"
        assert tpl_rtr.get((0, 1)) == "tata"
        assert tpl_rtr.get((1, 0)) == "titi"
        assert tpl_rtr.get((1, 1)) == "tutu"
        assert tpl_rtr.get((1, 2), default="wrong key again") == "wrong key again"
        assert tpl_rtr.get((1, 2)) is None
        assert tpl_rtr.get([1, 1], default="not a tuple key") == "not a tuple key"

    @pytest.mark.parametrize("test_file", [{"extension": "csv"}], indirect=True)
    def test_init_and_read_file(self, test_file):
        tpl_rtr1 = CsvTemplateRetriever(self.csv_content)
        self._check_get(tpl_rtr1)

        self.csv_content.to_csv(test_file.name)
        test_file.close()
        tpl_rtr2 = read_template(test_file.name, index_col=["A", "B"])
        self._check_get(tpl_rtr2)

        assert tpl_rtr1 == tpl_rtr2


class TestCentroidTemplateRetriever:

    csv_weights = [0.7, 0.25]
    csv_content = pd.DataFrame(
        [[0, 0, "toto"], [0, 1, "tata"], [1, 0, "titi"], [1, 1, "tutu"]],
        columns=["A", "B", "template"],
    )

    def _check_get(self, tpl_rtr):
        assert isinstance(tpl_rtr, CentroidTemplateRetriever)

        assert tpl_rtr.get([1, 2]) == "tutu"
        assert tpl_rtr.get([-1, 0.8]) == "tata"

        tpl_dict = tpl_rtr.get_by_dtw([1, 1, 1, 0, 0, 0, 0])
        assert tpl_dict["template"] == "titi"
        assert tpl_dict["centroid"] == (1, 0)

    @pytest.mark.parametrize("test_file", [{"extension": "csv"}], indirect=True)
    def test_init_and_read_file(self, test_file):
        tpl_rtr1 = CentroidTemplateRetriever(
            self.csv_content.set_index(["A", "B"]),
            col="template",
            weights=self.csv_weights,
        )
        self._check_get(tpl_rtr1)

        df = self.csv_content.copy()
        df.loc["weights"] = self.csv_weights + [None]
        df.to_csv(test_file.name)
        test_file.close()

        tpl_rtr2 = read_template(test_file.name)
        self._check_get(tpl_rtr2)

        assert tpl_rtr1 == tpl_rtr2
