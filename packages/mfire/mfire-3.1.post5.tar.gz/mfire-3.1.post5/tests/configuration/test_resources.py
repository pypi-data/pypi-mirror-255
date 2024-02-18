from pathlib import Path

from mfire.configuration.resources import (
    GridPointRHConfig,
    MaskRHConfig,
    PrometheeGridPointRHConfig,
    _DataResourceHandlerConfig,
    _ResourceHandlerConfig,
)

# Basic tests configuration


class Test_Resources:
    """New class for testing the config composite step"""

    def test_init(self):
        # on mémorise juste les varaibles
        result = _ResourceHandlerConfig(
            role="role",
            fatal=True,
            now=False,
            kind="kind",
            vapp="vapp",
            vconf="vconf",
            namespace="namespace",
            experiment="TEST",
            block="blcok",
            format="grib",
            local=Path("/"),
        )
        assert result
        result = _DataResourceHandlerConfig(
            model="model",
            date="2023-08-15",
            nativefmt="grib",
            geometry="franxl1s100",
            cutoff="production",
            origin="origin",
            kind="kind",
            vapp="vapp",
            vconf="vconf",
            namespace="namespace",
            experiment="TEST",
            block="blcok",
            format="grib",
            local=Path("/"),
        )
        assert result
        result = GridPointRHConfig(
            model="model",
            date="2023-08-15",
            nativefmt="grib",
            geometry="franxl1s100",
            cutoff="production",
            origin="origin",
            kind="gridpoint",
            vapp="vapp",
            vconf="vconf",
            namespace="namespace",
            experiment="TEST",
            block="blcok",
            format="grib",
            local=Path("/"),
            term=12,
        )
        assert result
        result = PrometheeGridPointRHConfig(
            model="model",
            date="2023-08-15",
            nativefmt="grib",
            geometry="franxl1s100",
            cutoff="production",
            origin="origin",
            kind="promethee_gridpoint",
            vapp="vapp",
            vconf="vconf",
            namespace="namespace",
            experiment="TEST",
            block="blcok",
            format="grib",
            local=Path("/"),
            param="EAU__SOL",
            begintime=12,
            endtime=48,
            step=1,
        )
        assert result
        result = MaskRHConfig(
            role="role",
            fatal=True,
            now=False,
            kind="promethee_mask",
            vapp="vapp",
            vconf="vconf",
            namespace="namespace",
            experiment="TEST",
            block="blcok",
            format="grib",
            local=Path("/"),
            promid="prom",
            version="v0",
        )
        assert result
