from pydantic import ValidationError

from mfire.configuration.configs import ConfigGlobal, VersionConfig

# Basic tests configuration


class Test_ConfigGlobal:
    def test_init(self):
        # on mémorise juste les varaibles
        result = ConfigGlobal("TEST", "H123", "settings", "rules", "get_geo", "compos")
        assert result
        result = VersionConfig(
            version="v0",
            drafting_datetime="20230815",
            reference_datetime="20230815",
            production_datetime="20230815",
            configuration_datetime="20230815",
        )
        assert result
        try:
            result = VersionConfig(
                version="v0",
                drafting_datetime="",
                reference_datetime="20230815",
                production_datetime="20230815",
                configuration_datetime="20230815",
            )
        except ValidationError:
            pass
