from silx.utils.enum import Enum as _Enum


class ReduceMethod(_Enum):
    """
    possible method to compute reduced darks / flats
    """

    MEAN = "mean"  # compute the mean of dark / flat frames serie
    MEDIAN = "median"  # compute the median of dark / flat frames serie
    FIRST = "first"  # take the first frame of the dark / flat serie
    LAST = "last"  # take the last frame of the dark / flat serie
    NONE = "none"
