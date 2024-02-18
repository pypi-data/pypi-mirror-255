from typing import Dict, List, Optional, Union

import numpy as np
from pydantic import BaseModel

import mfire.utils.mfxarray as xr
from mfire.composite import RiskComponentComposite
from mfire.composite.operators import ComparisonOperator
from mfire.localisation.localisation_manager import Localisation
from mfire.settings import MONOZONE, TEMPLATES_FILENAMES, get_logger
from mfire.text.comment.multizone import ComponentHandlerLocalisation
from mfire.text.template import CentroidTemplateRetriever, read_template
from mfire.utils.date import Datetime
from mfire.utils.exception import LocalisationError, LocalisationWarning

# Logging
LOGGER = get_logger(name="text_reducer.mod", bind="text_reducer")


class Reducer(BaseModel):
    """Reducer: Object managing all functionalities of the component
    necessary to create an appropriate comment.
    """

    module: str = "monozone"
    component: RiskComponentComposite
    reduction: Dict = {}

    def reset(self) -> None:
        """Resets the reduction dictionary."""
        self.reduction = {}

    def compute(self, geo_id: str, component: RiskComponentComposite) -> None:
        """
        Decides which comment generation module to use.

        Args:
            geo_id (str): Zone ID.
            component (RiskComponentComposite): Component under study.
        """
        maxi_risk = component.final_risk_max_level(geo_id)

        if maxi_risk >= 1:
            # Add other conditions to bypass localization.
            # - Risk type (upstream/downstream)

            # Get the risk definition
            risk_list = component.risks_of_level(level=maxi_risk)

            agg = risk_list[0].aggregation_type

            if agg == "downStream":
                hourly_maxi_risk = component.final_risk_da.sel(id=geo_id)
                # Get the period where the highest risk exists
                risk_period = hourly_maxi_risk.sel(
                    valid_time=(hourly_maxi_risk == maxi_risk)
                ).valid_time
                try:
                    # TODO: Refactor ComponentHandlerLocalization
                    # or Localisation if necessary
                    self.reduction = ComponentHandlerLocalisation(
                        localisation_handler=Localisation(
                            component,
                            risk_level=maxi_risk,
                            geo_id=geo_id,
                            period=set(risk_period.values),
                        )
                    )
                    unique_table, _ = self.reduction.get_summarized_info()
                    # On va regarder s'il est nécessaire de faire de
                    # la localisation spatiale sur le risque le plus eleve.
                    if unique_table.id.size > 1:
                        self.module = "multizone"
                        LOGGER.debug("Going to multiZone commentary type")
                        return None

                except LocalisationWarning as e:
                    # If it is a 'normal' error from the localization module
                    # (no descriptive zones, wrong risk type, etc.).
                    # Then switch to the monozone module.
                    LOGGER.warning(repr(e))
                except LocalisationError:
                    raise

        # Default case -> monozone
        self.reduce_monozone(geo_id)

    def get_operator_dict(self) -> Dict[str, Dict[str, str]]:
        """Get the comparison operators used for rounding the representative values.

        Returns:
            operator_dict (Dict): Dictionary containing the comparison operators per
                event.
        """
        operator_dict = {}
        for level in self.component.levels:
            for ev in level.elements_event:
                operator_dict[ev.field.name] = {}
                try:
                    operator_dict[ev.field.name]["plain"] = ev.plain.comparison_op
                except AttributeError:
                    pass
                try:
                    operator_dict[ev.field.name]["mountain"] = ev.mountain.comparison_op
                except AttributeError:
                    pass
        return operator_dict

    def get_rep_value(self, values: List[float], operator: ComparisonOperator) -> float:
        """Return the representative value based on the comparison operator.

        Args:
            values (List): List of representative values for each deadline.
            operator (ComparisonOperator): Comparison operator.

        Returns:
            float: The representative value.
        """
        if operator in (
            ComparisonOperator.SUP,
            ComparisonOperator.SUPEGAL,
        ):
            return max(values)
        if operator in (
            ComparisonOperator.INF,
            ComparisonOperator.INFEGAL,
        ):
            return min(values)

        LOGGER.warning(
            f"get_rep_value: unknown case {operator}",
            func="get_representative_values",
        )
        return np.NaN

    def get_template_type(self, bloc: Dict, reduced_risk: List) -> None:
        """
        Determines the template type (general, snow or precip).

        Args:
            bloc (Dict): Reduction block.
            reduced_risk (List): Reduced risks.
        """
        bloc_copy = {
            k: v
            for k, v in bloc.items()
            if k not in ["level", "start", "stop", "centroid_value"]
        }

        if max(reduced_risk) == bloc["level"]:
            evs = set()
            for ev in bloc_copy.keys():
                if "PRECIP" in ev or "EAU" in ev:
                    evs.add("PRECIP")
                elif "NEIPOT" in ev:
                    evs.add("SNOW")
                else:
                    evs.add(ev)

            if evs == {"PRECIP"}:
                self.reduction["type"] = "PRECIP"
            elif evs == {"SNOW"}:
                self.reduction["type"] = "SNOW"
            elif evs == {"PRECIP,SNOW"}:
                self.reduction["type"] = "PRECIP_SNOW"
            else:
                self.reduction["type"] = "general"

    def process_value(
        self, param: str, events: List, operator_dict: Dict, ev_type: str
    ) -> Optional[Dict]:
        """
        Retrieves all significant values (min, max, rep_value, units, etc.)
        for plain or mountain (ev_type argument).

        Args:
            param (str): Parameter (e.g., NEIPOT24__SOL).
            events (List): List of datasets containing events for a parameter.
            operator_dict (Dict): Dictionary containing comparison operators.
            ev_type (str): Plain or mountain.

        Returns:
            Dict: Dictionary containing the information or None if the information is
                not available (e.g., for a qualitative parameter or when ev_type is
                mountain but no mountain is available).
        """
        vars = events[0].data_vars
        min_v, max_v, rep_value, threshold = np.NaN, np.NaN, np.NaN, np.NaN
        occurrence_event, units, operator = False, np.NaN, np.NaN

        if (
            "min_" + ev_type in vars
            and "max_" + ev_type in vars
            and "rep_value_" + ev_type in vars
            and ev_type in operator_dict[param]
        ):
            ev_values = []
            for ev in events:
                occurrence_event = occurrence_event or ev["occurrence_event"]
                if ev["min_" + ev_type].values < min_v or np.isnan(min_v):
                    min_v = ev["min_" + ev_type].values

                if ev["max_" + ev_type].values > max_v or np.isnan(max_v):
                    max_v = ev["max_" + ev_type].values

                ev_values.append(ev["rep_value_" + ev_type].values)

            units = str(events[0].units.values)
            threshold = events[0][f"threshold_{ev_type}"]

            rep_value = self.get_rep_value(
                values=ev_values, operator=operator_dict[param][ev_type]
            )

            operator = operator_dict[param][ev_type]

        values_dict = {
            "min": None if (min_v == "nan" or np.isnan(min_v)) else float(min_v),
            "max": None if (max_v == "nan" or np.isnan(max_v)) else float(max_v),
            "value": None
            if (rep_value == "nan" or np.isnan(rep_value))
            else float(rep_value),
            "units": units,
            "operator": operator,
            "threshold": threshold,
            "occurrence_event": occurrence_event,
        }

        if None in values_dict.values():
            return None

        return values_dict

    def get_infos(self, data: List[xr.Dataset]) -> dict:
        """
        Retrieves the information for each block Bi.

        Args:
            data (List[xr.Dataset]): List of data arrays for the same level.

        Returns:
            dict: Dictionary summarizing the desired information.
        """
        bloc = {}

        if isinstance(data[0], xr.DataArray):
            bloc["level"] = 0
            time = [ech.values for ech in data]
            bloc["start"] = Datetime(min(time))
            bloc["stop"] = Datetime(max(time))
        else:
            operator_dict = self.get_operator_dict()
            event_dict = {}
            time = []

            for ech in data:
                time.append(ech.valid_time.values)
                for ev in ech.evt:
                    event = ech.sel(evt=ev)
                    key_event = str(event.weatherVarName.values)
                    if key_event != "nan":
                        if key_event in event_dict:
                            event_dict[key_event].append(event)
                        else:
                            event_dict[key_event] = [event]

            for k, v in event_dict.items():
                if k != "nan":
                    bloc[k] = {}

                    plain = self.process_value(k, v, operator_dict, "plain")
                    if plain:
                        bloc[k]["plain"] = {**plain}

                    mountain = self.process_value(k, v, operator_dict, "mountain")
                    if mountain:
                        bloc[k]["mountain"] = {**mountain}

            bloc["level"] = int(data[0].risk_level.values)
            bloc["start"] = Datetime(min(time))
            bloc["stop"] = Datetime(max(time))

        return bloc

    def reduce_risk(
        self, final_risk: xr.DataArray, component: xr.Dataset
    ) -> Union[List, dict]:
        """
        Reduces the risk into blocks based on the blocks found after using dtw.

        Args:
            final_risk (xr.DataArray): Risk data array.
            component (xr.Dataset): Dataset containing the information to extract
                during reduction.

        Returns:
            Union[List, dict]: Reduced risk as a list and a dictionary containing
                information for each block.
        """
        final_risk["blocks"] = ("valid_time", [v[1] for v in self.reduction["path"]])

        centroid_list = []
        last = final_risk["blocks"].values[0]

        for x in final_risk["blocks"].values:
            if last == x:
                centroid_list.append(self.reduction["centroid"][last])
            else:
                centroid_list.append(self.reduction["centroid"][last + 1])
            last = x

        final_risk["centroid"] = ("valid_time", centroid_list)

        actives_levels = component["risk_level"].values

        reduction = self.reduction
        previous_centroid = final_risk["centroid"].values[0]
        previous_block = final_risk["blocks"].values[0]
        same_level_list = []

        for i, level in enumerate(final_risk):
            if i == len(final_risk) - 1:
                if previous_centroid != level["centroid"].values:
                    reduction[f"B{previous_block}"] = self.get_infos(same_level_list)
                    reduction[f"B{previous_block}"][
                        "centroid_value"
                    ] = previous_centroid
                    if level["centroid"].values == 0:
                        reduction[f"B{level['blocks'].values}"] = self.get_infos(
                            [level["valid_time"]]
                        )
                    elif level.values in actives_levels:
                        reduction[f"B{level['blocks'].values}"] = self.get_infos(
                            [
                                component.sel(
                                    valid_time=level["valid_time"],
                                    risk_level=level.values,
                                )
                            ]
                        )

                    reduction[f"B{level['blocks'].values}"]["centroid_value"] = level[
                        "centroid"
                    ].values
                else:
                    if level["centroid"].values == 0:
                        same_level_list.append(level["valid_time"])
                    elif level.values in actives_levels:
                        same_level_list.append(
                            component.sel(
                                valid_time=level["valid_time"],
                                risk_level=level.values,
                            )
                        )

                    reduction[f"B{previous_block}"] = self.get_infos(same_level_list)
                    reduction[f"B{previous_block}"][
                        "centroid_value"
                    ] = previous_centroid
                break
            if previous_centroid == level["centroid"].values:
                if level["centroid"].values == 0:
                    same_level_list.append(level["valid_time"])
                elif level.values in actives_levels:
                    same_level_list.append(
                        component.sel(
                            valid_time=level["valid_time"],
                            risk_level=level.values,
                        )
                    )

                previous_centroid = level["centroid"].values
                previous_block = level["blocks"].values
            else:
                reduction[f"B{previous_block}"] = self.get_infos(same_level_list)
                same_level_list = []
                if level["centroid"].values == 0:
                    same_level_list.append(level["valid_time"])
                elif level.values in actives_levels:
                    same_level_list.append(
                        component.sel(
                            valid_time=level["valid_time"],
                            risk_level=level.values,
                        )
                    )

                reduction[f"B{previous_block}"]["centroid_value"] = previous_centroid
                previous_centroid = level["centroid"].values
                previous_block = level["blocks"].values

        reduced_risk = [v["level"] for k, v in reduction.items() if isinstance(v, dict)]
        reduction["reduced"] = reduced_risk
        reduction[
            "compo_hazard"
        ] = f"{self.component.name}_{self.component.hazard_name}"
        reduction["production_datetime"] = self.component.production_datetime

        return reduced_risk, reduction

    def compare_val(self, max_val: dict, level: str, data: dict, key: str) -> bool:
        """Compare the representative values of plain or, if they are equal, mountain.

        Args:
            max_val (dict): Dictionary of the highest representative values currently.
            level (str): Level.
            data (dict): Data to compare.
            key (str): Parameter (e.g., EAU1__SOL).

        Returns:
            bool: True if the value in max is the highest, False otherwise.
        """
        operators = self.get_operator_dict()

        try:
            operator = ComparisonOperator(operators[key]["plain"]).strict
            if not operator.is_order:
                return False

            if operator(
                max_val[level][key]["plain"]["value"],
                data["plain"]["value"],
            ):
                return True
            elif max_val[level][key]["plain"]["value"] != data["plain"]["value"]:
                return False
        except KeyError:
            pass

        try:
            operator = ComparisonOperator(operators[key]["mountain"]).strict
            if not operator.is_order:
                return False

            return operator(
                max_val[level][key]["mountain"]["value"],
                data["mountain"]["value"],
            )
        except KeyError:
            return True

    def get_levels_val(self):
        """Add information about the maximum and intermediate levels to the reduction.
        This is done by comparing the representative values for the same parameter at
        the same level.
        """
        max_val = {"level_max": {}, "level_int": {}}

        for bloc, data in self.reduction.items():
            if bloc.startswith("B"):
                # Create a copy of data without certain keys
                data_copy = {
                    k: v
                    for k, v in data.items()
                    if k not in ["level", "start", "stop", "centroid_value"]
                }
                if data["centroid_value"] == 1:
                    for key, param in data_copy.items():
                        if key in max_val["level_max"] and self.compare_val(
                            max_val, "level_max", param, key
                        ):
                            pass
                        else:
                            max_val["level_max"][key] = param
                elif data["level"] == 0:
                    pass
                else:
                    for key, param in data_copy.items():
                        if key in max_val["level_int"] and self.compare_val(
                            max_val, "level_int", param, key
                        ):
                            pass
                        else:
                            max_val["level_int"][key] = param
        for level, data in max_val.items():
            self.reduction[level] = data

    def compute_distance(self, norm_risk: List, method: str = "random"):
        """Searches the monozone matrix to determine the template
        using Dynamic Time Warping (DTW) and finds the lowest distance.

        Args:
            norm_risk (list): Normalized risk levels.
            method (str): Method for selecting the template (default is "random").

        Updates the reduction with information about the chosen centroid:
        {
            "distance": ,
            "path": ,
            "template": ,
            "centroid": ,
            "type":
        }
        """
        template_retriever = CentroidTemplateRetriever.read_file(
            MONOZONE, index_col=["0", "1", "2", "3", "4"]
        )
        self.reduction.update(
            template_retriever.get_by_dtw(norm_risk, pop_method=method)
        )

    def reduce_monozone(self, geo_id: str) -> None:
        """Reduces the information for the monozone case to a single vector.

        Args:
            geo_id (str): Zone ID.
        """
        self.reset()
        final_risk = self.component.final_risk_da.sel(id=geo_id)
        component = self.component.risks_ds.sel(id=geo_id)

        risk_max = max(final_risk.values)
        risk_min = min(final_risk.values)
        level_max = max(component.risk_level.values)

        # Normalize risk levels
        norm_risk = final_risk.values
        if level_max > 1:
            norm_risk = np.where(
                norm_risk, 1 - (((level_max - norm_risk) * 0.5) / (level_max - 1)), 0
            )

        # Use DTW to approximate a template
        self.compute_distance(norm_risk=norm_risk)

        # Reduce the risk in blocks
        reduced_risk, self.reduction = self.reduce_risk(final_risk, component)
        self.reduction["risk_max"] = risk_max
        self.reduction["risk_min"] = risk_min
        self.reduction["level_maxi"] = level_max

        self.get_levels_val()

        # Find the template type
        for key, bloc in self.reduction.items():
            if key.startswith("B"):
                if bloc["level"] == risk_max and bloc["level"] != 0:
                    self.get_template_type(bloc, reduced_risk)

        if self.reduction["type"] != "general":
            template_retriever = read_template(
                TEMPLATES_FILENAMES["fr"]["monozone"]["precip"]
            )
            default = (
                "Failed to retrieve the template"
                f"(key={self.reduction['type']}) (error COM-001)."
            )
            self.reduction["template"] = template_retriever.get(
                key=self.reduction["type"], default=default
            )
