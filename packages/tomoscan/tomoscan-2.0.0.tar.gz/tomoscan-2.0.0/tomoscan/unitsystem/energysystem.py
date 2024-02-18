from tomoscan.utils.io import deprecated_warning

deprecated_warning(
    type_="Module",
    name="tomoscan.unitsystem.energysystem",
    reason="dedicated project created",
    replacement="pyunitsystem.energysystem",
    since_version="2.0",
)

from pyunitsystem.energysystem import *  # noqa F401
