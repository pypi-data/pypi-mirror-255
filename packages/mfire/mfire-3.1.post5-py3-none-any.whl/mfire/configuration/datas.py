"""
@package configuration.datas

data for Config processor module
"""

# Standard packages
from typing import Optional

from pydantic import BaseModel

from mfire import composite
from mfire.configuration.rules import Rules

# Own package
from mfire.settings import LOCAL, Settings, get_logger
from mfire.utils.date import Datetime, Timedelta, int_timedelta
from mfire.utils.string_utils import TagFormatter

# Third parties packages


# local package

# Logging
LOGGER = get_logger(name="config_processor.mod", bind="config_processor")

DEFAULT_TIME_DIMENSION = "valid_time"  # TODO: put it in the csv settings files
DEFAULT_COMPUTE_LIST = ["density", "extrema", "representative", "summary"]

EventComposites = composite.EventComposite | composite.EventBertrandComposite
ComponentComposites = (
    composite.RiskComponentComposite | composite.TextComponentComposite
)


class RHManager(BaseModel):
    rules: Rules

    def get_settings(self):
        """
        Function present to be mocked by tests
        to change reference directory
        """
        return Settings()

    def create_rh(
        self,
        file_id: str,
        term: Datetime,
        param: str,
        alternate: tuple = None,
    ) -> dict:
        # basic infos from dataframe
        file_info = self.rules.get_file_info(file_id)

        # resource_handler
        resource_columns = [
            "kind",
            "model",
            "date",
            "geometry",
            "cutoff",
            "origin",
            "nativefmt",
        ]
        settings = self.get_settings()
        rh_dico = file_info[resource_columns].to_dict()
        rh_dico["date"] = str(Datetime(file_info["date"]))
        rh_dico["vapp"] = file_info.get("vapp", settings.vapp)
        rh_dico["vconf"] = file_info.get("vconf", settings.vconf)
        rh_dico["experiment"] = file_info.get("experiment", settings.experiment)
        rh_dico["block"] = file_info["block"]
        rh_dico["namespace"] = file_info["namespace"]
        rh_dico["format"] = file_info["nativefmt"]

        # case if we create a source rh
        if file_id in self.rules.source_files_df.index and term is not None:
            rh_dico["term"] = int_timedelta(file_info["date"], term)
            role_name = f"{file_id} {term}"

        # case if we create a preprocessed rh
        elif file_id in self.rules.preprocessed_files_df.index and param is not None:
            rh_dico["param"] = param
            rh_dico["begintime"] = int_timedelta(file_info["date"], file_info["start"])
            rh_dico["endtime"] = int_timedelta(file_info["date"], file_info["stop"])
            rh_dico["step"] = int(file_info["step"])
            role_name = f"{file_id} {param}"

        # role or alternate
        if alternate is None:
            rh_dico["local"] = settings.data_dirname / TagFormatter().format_tags(
                LOCAL[file_info["kind"]], rh_dico
            )
            rh_dico["role"] = role_name

        else:
            rh_dico["alternate"], rh_dico["local"] = alternate

        rh_dico["fatal"] = False
        rh_dico["now"] = True
        return rh_dico

    def create_full_file_config(
        self, file_id: str, term: Datetime = None, param: str = None
    ) -> list:
        """Creates a list of resource handlers with all the alternate files for a
        given file_id

        Args:
            file_id (str): name of the file
            term (Datetime, optional): requeseted term. Defaults to None.
            param (str, optional): requested parameter. Defaults to None.

        Returns:
            list: _description_
        """
        # creating main resource handler
        role_rh = self.create_rh(file_id, term=term, param=param)
        resource_handlers = [role_rh]

        # adding alternates
        current_file_id = file_id

        for _ in range(self.get_settings().alternate_max):

            current_file_id = self.rules.get_alternate(current_file_id)

            if current_file_id not in self.rules.files_ids:
                break

            resource_handlers += [
                self.create_rh(
                    current_file_id,
                    term=term,
                    param=param,
                    alternate=(role_rh["role"], role_rh["local"]),
                )
            ]

        return resource_handlers

    def preprocessed_rh(self, file_id, param):
        """resource handler"""

        return self.create_full_file_config(file_id, param=param)

    def source_files_terms(
        self, data_config: dict, file_id: str, param: str, accum: Optional[int]
    ) -> dict:
        """source_files_terms : Returns source files id and term needed for a given
        preprocessed file id, a complete parameter name, an accumulation period
        and start/stop datetimes. It also computes the source files configurations
        and stores them into the self.data_config['sources'].

        Args:
            file_id (str): Preprocessed file id
            param (str): Complete Parameter name
            accum (Optional[int]): Accumulation period in hours

        Returns:
            dict : Dictionnary with the following structure :
                {
                    <source_file_id> : [terms]
                }
        """
        preprocessed_file_info = self.rules.get_file_info(file_id)
        source_files_list = [
            source_file_id.strip()
            for source_file_id in self.rules.files_links_df.loc[param, file_id].split(
                ","
            )
        ]
        source_files_dico = dict()
        current_start = preprocessed_file_info["start"]
        # Adding virtual terms due to accumulation (for preproc files)
        preproc_stop = preprocessed_file_info["stop"]
        preproc_step = Timedelta(hours=int(preprocessed_file_info["step"]))
        accum_td = Timedelta(hours=int(accum)) if accum is not None else Timedelta(0)
        virtual_stop = preproc_stop + accum_td
        virtual_range = range(1, int((virtual_stop - preproc_stop) / preproc_step) + 1)
        virtual_terms = [preproc_stop + preproc_step * i for i in virtual_range]
        for source_file_id in source_files_list:
            # We check until virtual stop in case of accumulation
            if virtual_stop <= current_start:
                break
            if source_file_id not in self.rules.source_files_df.index:
                continue
            source_file_info = self.rules.get_file_info(source_file_id)
            source_files_dico[source_file_id] = {
                "terms": [
                    int_timedelta(source_file_info["date"], term)
                    for term in source_file_info["terms"]
                    if (
                        term >= current_start
                        and term in preprocessed_file_info["terms"] + virtual_terms
                    )
                ],
                "step": int(source_file_info["step"]),
            }
            current_start = source_file_info["terms"][-1] + preproc_step

            if source_file_id in data_config["sources"]:
                continue
            data_dico = dict()  # intermediary dict for parallelism
            for term in source_file_info["terms"]:
                term_int = int_timedelta(source_file_info["date"], term)
                data_dico[term_int] = self.create_full_file_config(
                    file_id=source_file_id, term=term
                )
            # "sources" is managed for parallelism : just its direct update is reported
            # here a new key/value is created
            data_config["sources"][source_file_id] = data_dico
            # the value is a dict :
            # all changes to this dict after this point won't be report
        return source_files_dico

    def __str__(self):
        return f"{self.rules}"
