from tomoscan.utils.io import deprecated_warning

deprecated_warning(
    type_="Module",
    name="tomoscan.unitsystem.timesystem",
    reason="dedicated project created",
    replacement="pyunitsystem.timesystem",
    since_version="2.0",
)

from pyunitsystem.timesystem import *  # noqa F401
