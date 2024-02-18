"""deprecated module. Use 'pyunitsystem' instead"""

from tomoscan.utils.io import deprecated_warning

from silx.utils.enum import Enum as _Enum

from pyunitsystem.electriccurrentsystem import (
    ElectricCurrentSystem as _ElectricCurrentSystem,
)
from pyunitsystem.energysystem import EnergySI as _EnergySI
from pyunitsystem.metricsystem import MetricSystem as _MetricSystem
from pyunitsystem.timesystem import TimeSystem as _TimeSystem
from pyunitsystem.unit import Unit as _Unit


class ElectricCurrentSystem(_Enum):
    def __getattribute__(self, name):
        deprecated_warning(
            type_="Module",
            name="tomoscan.unitsystem",
            reason="dedicated project created",
            replacement="pyunitsystem",
            since_version="2.0",
        )
        return _ElectricCurrentSystem.__getattribute__(self, name)


class EnergySI(_Enum):
    def __getattribute__(self, name):
        deprecated_warning(
            type_="Module",
            name="tomoscan.unitsystem",
            reason="dedicated project created",
            replacement="pyunitsystem",
            since_version="2.0",
        )
        return _EnergySI.__getattribute__(self, name)


class MetricSystem(_Enum):
    def __getattribute__(self, name):
        deprecated_warning(
            type_="Module",
            name="tomoscan.unitsystem",
            reason="dedicated project created",
            replacement="pyunitsystem",
            since_version="2.0",
        )
        return _MetricSystem.__getattribute__(self, name)


class TimeSystem(_Enum):
    def __getattribute__(self, name):
        deprecated_warning(
            type_="Module",
            name="tomoscan.unitsystem",
            reason="dedicated project created",
            replacement="pyunitsystem",
            since_version="2.0",
        )
        return _TimeSystem.__getattribute__(self, name)


class Unit(_Enum):
    def __getattribute__(self, name):
        deprecated_warning(
            type_="Module",
            name="tomoscan.unitsystem",
            reason="dedicated project created",
            replacement="pyunitsystem",
            since_version="2.0",
        )
        return _Unit.__getattribute__(self, name)
