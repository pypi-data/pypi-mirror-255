import mfire.utils.mfxarray as xr
from mfire.text.comment.multizone import ComponentInterface
from mfire.utils.date import Datetime


class ComponentInterfaceFactory(ComponentInterface):
    log_ids = {}
    template_key = "key"
    template_type = "type"
    production_datetime = Datetime(2023, 3, 1)
    periods_name = []
    areas_name = []
    merged_area = xr.DataArray()
    critical_value = {}
    risk_name = "risk_name"

    def get_template_key(self) -> str:
        return self.template_key

    def get_template_type(self) -> str:
        return self.template_type

    def get_production_datetime(self) -> Datetime:
        return self.production_datetime

    def get_periods_name(self):
        return self.periods_name

    def get_areas_name(self):
        return self.areas_name

    def merge_area(self, **kwargs) -> xr.DataArray:
        return self.merged_area

    def get_critical_value(self) -> dict:
        return self.critical_value

    def get_risk_name(self) -> str:
        return self.risk_name

    @classmethod
    def open(cls, **kwargs):
        pass
