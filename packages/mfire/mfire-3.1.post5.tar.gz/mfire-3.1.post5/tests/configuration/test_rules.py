import numpy as np
import pandas as pd
import pytest

from mfire.configuration.rules import Rules
from mfire.settings import RULES_NAMES
from mfire.utils.date import Datetime, Timedelta
from mfire.utils.exception import ConfigurationError, ConfigurationWarning

PREPROCESSED_COLUMNS = {
    "kind",
    "model",
    "date",
    "time_ref",
    "geometry",
    "cutoff",
    "origin",
    "nativefmt",
    "start",
    "stop",
    "step",
    "dispo_time",
    "block",
    "namespace",
    "alternate",
}

SOURCES_COLUMNS = PREPROCESSED_COLUMNS.union({"vapp", "vconf", "experiment"})

DRAFTING_DATETIME = Datetime(2022, 1, 1, 8, 31, 12)


class TestSettingsRules:
    """Classe qui teste les fichiers de configuration des données météos"""

    def test_init(self):
        """teste l'initialisation de la classe Rules"""
        for rules_name in RULES_NAMES:
            rules = Rules(name=rules_name, drafting_datetime=DRAFTING_DATETIME)
            # grib_param
            assert isinstance(rules.grib_param_df, pd.DataFrame)
            # agg_param
            assert isinstance(rules.agg_param_df, pd.DataFrame)
            # param_link
            assert isinstance(rules.param_link_df, pd.DataFrame)
            assert set(rules.param_link_df.index) == set(rules.param_link_df)
            assert set(rules.param_link_df.index).issubset(
                rules.grib_param_df.index.levels[0]
            )
            # geometries
            assert isinstance(rules.geometries_df, pd.DataFrame)
            # source_files
            assert isinstance(rules.source_files_df, pd.DataFrame)
            # preprocessed_files
            assert isinstance(rules.preprocessed_files_df, pd.DataFrame)
            # files_links
            assert isinstance(rules.files_links_df, pd.DataFrame)
            assert set(rules.param_link_df.index) == set(rules.files_links_df.index)

    def test_content_files_links(self):
        """Teste le contenu des fichiers files_links et source_files
        Sauf pour la primière ligne, première colonne les champs indiqués
        dans le fichier  files_links sont présents dans la colonne filename
        de source_files
        """
        for rules_name in RULES_NAMES:
            for td in range(25):
                drafting_datetime = DRAFTING_DATETIME + Timedelta(hours=td)
                rules = Rules(name=rules_name, drafting_datetime=drafting_datetime)

                assert PREPROCESSED_COLUMNS.issubset(rules.preprocessed_files_df)
                assert SOURCES_COLUMNS.issubset(rules.source_files_df)

                # vérification que tous les files ids dans files_links existent
                fileids = set(
                    rules.files_links_df[
                        rules.preprocessed_files_df.index
                    ].values.flatten()
                )
                source_fileids = []
                for fileid in fileids:
                    if isinstance(fileid, float):
                        assert np.isnan(fileid)
                        continue
                    source_fileids.extend(fileid.split(","))

                assert set(source_fileids).issubset(rules.source_files_df.index)

    def test_best_preprocessed_files(self):
        """Test l'execution de la fonction best_preprocessed_files."""
        rules = Rules(name="psym", drafting_datetime=DRAFTING_DATETIME)
        geometries = list(rules.geometries_df.index)
        params = list(rules.param_link_df)[:2]
        with pytest.raises(ConfigurationWarning) as exc_info:
            rules.best_preprocessed_files(
                start=Datetime(2022, 1, 1, 0),
                stop=Datetime(2022, 1, 1, 6),
                geometries=geometries,
                params=params,
            )
        assert isinstance(exc_info.value, ConfigurationWarning)

        best = rules.best_preprocessed_files(
            start=Datetime(2022, 1, 1, 0),
            stop=Datetime(2022, 1, 2, 0),
            geometries=geometries,
            params=params,
        )
        assert best == [
            (
                "france_jj1_2022-01-01T00:00:00+00:00_08",
                "2022-01-01T09:00:00+00:00",
                "2022-01-02T00:00:00+00:00",
            )
        ]

        best = rules.best_preprocessed_files(
            start=Datetime(2022, 1, 1, 0),
            stop=Datetime(2022, 1, 10, 0),
            geometries=geometries,
            params=params,
        )

        assert best == [
            (
                "france_jj1_2022-01-01T00:00:00+00:00_08",
                "2022-01-01T09:00:00+00:00",
                "2022-01-03 00:00:00+00:00",
            ),
            (
                "france_j2j3_2022-01-01T00:00:00+00:00_08",
                "2022-01-03 03:00:00+00:00",
                "2022-01-05 00:00:00+00:00",
            ),
            (
                "monde_j4j14_2021-12-31T00:00:00+00:00_maj22",
                "2022-01-05 03:00:00+00:00",
                "2022-01-10T00:00:00+00:00",
            ),
        ]

        best = rules.best_preprocessed_files(
            start=Datetime(2022, 1, 3, 1),
            stop=Datetime(2022, 1, 10, 0),
            geometries=geometries,
            params=params,
        )

        assert best == [
            (
                "france_j2j3_2022-01-01T00:00:00+00:00_08",
                "2022-01-03T03:00:00+00:00",
                "2022-01-05 00:00:00+00:00",
            ),
            (
                "monde_j4j14_2021-12-31T00:00:00+00:00_maj22",
                "2022-01-05 03:00:00+00:00",
                "2022-01-10T00:00:00+00:00",
            ),
        ]
        with pytest.raises(ConfigurationError) as exc_info:

            rules.best_preprocessed_files(
                start=Datetime(2022, 2, 10, 0),
                stop=Datetime(2022, 2, 11, 0),
                geometries=geometries,
                params=params,
            )
            print(rules)
        assert isinstance(exc_info.value, ConfigurationError)
