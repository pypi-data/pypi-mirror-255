from tomoscan.utils.io import deprecated_warning

deprecated_warning(
    type_="Module",
    name="tomoscan.unitsystem.metricsystem",
    reason="dedicated project created",
    replacement="pyunitsystem.metricsystem",
    since_version="2.0",
)

from pyunitsystem.metricsystem import *  # noqa F401
