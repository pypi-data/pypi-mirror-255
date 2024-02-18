from tomoscan.utils.io import deprecated_warning

deprecated_warning(
    type_="Module",
    name="tomoscan.unitsystem.unit",
    reason="dedicated project created",
    replacement="pyunitsystem.unit",
    since_version="2.0",
)

from pyunitsystem.unit import *  # noqa F401
