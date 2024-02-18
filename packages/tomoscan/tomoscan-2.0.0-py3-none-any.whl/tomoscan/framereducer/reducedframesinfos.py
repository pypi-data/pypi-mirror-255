import numpy
from typing import Optional, Iterable


class ReducedFramesInfos:
    """contains reduced frames metadata as count_time and machine_electric_current"""

    MACHINE_ELECT_CURRENT_KEY = "machine_electric_current"

    COUNT_TIME_KEY = "count_time"

    def __init__(self) -> None:
        self._count_time = []
        self._machine_electric_current = []

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, dict):
            return ReducedFramesInfos().load_from_dict(__o) == self
        if not isinstance(__o, ReducedFramesInfos):
            return False
        return numpy.array_equal(
            numpy.array(self.count_time), numpy.array(__o.count_time)
        ) and numpy.array_equal(
            numpy.array(self.machine_electric_current),
            numpy.array(__o.machine_electric_current),
        )

    def clear(self):
        self._count_time.clear()
        self._machine_electric_current.clear()

    @property
    def count_time(self) -> list:
        """
        frame exposure time in second
        """
        return self._count_time

    @count_time.setter
    def count_time(self, count_time: Optional[Iterable]):
        if count_time is None:
            self._count_time.clear()
        else:
            self._count_time = list(count_time)

    @property
    def machine_electric_current(self) -> list:
        """
        machine electric current in Ampere
        """
        return self._machine_electric_current

    @machine_electric_current.setter
    def machine_electric_current(self, machine_electric_current: Optional[Iterable]):
        if machine_electric_current is None:
            self._machine_electric_current.clear()
        else:
            self._machine_electric_current = list(machine_electric_current)

    def to_dict(self) -> dict:
        res = {}
        if len(self.machine_electric_current) > 0:
            res[self.MACHINE_ELECT_CURRENT_KEY] = self.machine_electric_current
        if len(self.count_time) > 0:
            res[self.COUNT_TIME_KEY] = self.count_time
        return res

    def load_from_dict(self, my_dict: dict):
        self.machine_electric_current = my_dict.get(
            self.MACHINE_ELECT_CURRENT_KEY, None
        )
        self.count_time = my_dict.get(self.COUNT_TIME_KEY, None)
        return self

    @staticmethod
    def pop_info_keys(my_dict: dict):
        if not isinstance(my_dict, dict):
            raise TypeError
        my_dict.pop(ReducedFramesInfos.MACHINE_ELECT_CURRENT_KEY, None)
        my_dict.pop(ReducedFramesInfos.COUNT_TIME_KEY, None)
        return my_dict

    @staticmethod
    def split_data_and_metadata(my_dict):
        metadata = ReducedFramesInfos().load_from_dict(my_dict)
        data = ReducedFramesInfos.pop_info_keys(my_dict)
        return data, metadata

    def __str__(self):
        return "\n".join(
            [
                f"machine_electric_current {self.machine_electric_current}",
                f"count_time {self.count_time}",
            ]
        )
