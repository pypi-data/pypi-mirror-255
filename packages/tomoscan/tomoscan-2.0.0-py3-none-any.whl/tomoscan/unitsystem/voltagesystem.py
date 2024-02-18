from tomoscan.utils.io import deprecated_warning

deprecated_warning(
    type_="Module",
    name="tomoscan.unitsystem.voltagesystem",
    reason="dedicated project created",
    replacement="pyunitsystem.voltagesystem",
    since_version="2.0",
)

from pyunitsystem.voltagesystem import *  # noqa F401
