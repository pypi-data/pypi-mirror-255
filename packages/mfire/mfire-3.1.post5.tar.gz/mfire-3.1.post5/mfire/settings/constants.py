from pathlib import Path
from typing import Optional, Sequence, Union

# Paths
CUR_DIR = Path(".")
SETTINGS_DIR = Path(__file__).absolute().parent

# Rules
RULES_DIR = SETTINGS_DIR / "rules"
RULES_NAMES = tuple(
    d.name for d in RULES_DIR.iterdir() if d.is_dir() and not d.name.startswith("__")
)

# Text
_text_dir = SETTINGS_DIR / "text"
TEMPLATES_FILENAMES = {
    "fr": {
        "language": _text_dir / "fr" / "language.json",
        "date": _text_dir / "fr" / "date.json",
        "synonyms": _text_dir / "fr" / "synonyms.json",
        "period": _text_dir / "fr" / "period.csv",
        "multizone": {
            "generic": _text_dir / "comment" / "multizone.json",
            "snow": _text_dir / "comment" / "multizone_snow.json",
            "precip": _text_dir / "comment" / "multizone_precip.json",
            "rep_val_FFRaf": _text_dir / "comment" / "multizone_rep_value_FFRaf.json",
            "rep_val": _text_dir / "comment" / "multizone_rep_value.json",
            "rep_val_snow_bertrand": _text_dir
            / "comment"
            / "multizone_rep_value_snow_bertrand.json",
        },
        "monozone": {
            "precip": _text_dir / "comment" / "monozone_precip.json",
        },
        "synthesis": {
            "temperature": _text_dir / "synthesis" / "temperature.json",
            "weather": _text_dir / "synthesis" / "weather.json",
        },
        "situation_generale": _text_dir / "fr" / "sit_gen_templates.json",
        "compass": _text_dir / "fr" / "compass.json",
    },
    "en": {
        "date": _text_dir / "en" / "date.json",
        "compass": _text_dir / "fr" / "compass.json",
    },
}

MONOZONE = _text_dir / "comment" / "monozone.csv"

SIT_GEN = {
    "zones": {
        "front": SETTINGS_DIR / "geos/marine/zones_SG_anticyc_front.geojson",
        "anticyclone": SETTINGS_DIR / "geos/marine/zones_SG_anticyc_front.geojson",
        "depression": SETTINGS_DIR / "geos/marine/zones_SG_depression.geojson",
    },
    "depression": {
        "fast": (8, 16),
        "slow": (4, 8),
        "evol": (2, 4),
        "move": (200, 400),
    },
    "anticyclone": {
        "evol": (8, 16),
        "move": (400, 800),
    },
}

# Data conf
LOCAL = {
    "gridpoint": "[date:stdvortex]/[block]/[geometry:area]/[term:fmth].[format]",
    "promethee_gridpoint": (
        "[date:stdvortex]/[model]/[geometry:area]/"
        "[param].[begintime:fmth]_[endtime:fmth]_[step:fmth].[format]"
    ),
}

# Units
_units_dir = SETTINGS_DIR / "units"
UNITS_TABLES = {
    "pint_extension": _units_dir / "pint_extension.txt",
    "wwmf_w1": _units_dir / "wwmf_w1_correspondence.csv",
}

# Default altitudes min and max
ALT_MIN = -500
ALT_MAX = 10000
EARTH_RADIUS_KM = 6378.137

# Default dimensions used
Dimension = Optional[Union[str, Sequence[str]]]
SPACE_DIM = ("latitude", "longitude")
TIME_DIM = ("valid_time",)

# Localisation default values
N_CUTS = 2
GAIN_THRESHOLD = 0.001
