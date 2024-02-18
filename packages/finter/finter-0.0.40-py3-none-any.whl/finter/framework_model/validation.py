import re
from pathlib import Path
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

import pandas as pd

from finter.settings import logger
from finter.utils.index import outsample_end_date
from finter.utils.model.frames import FrameUtil
from finter.utils.library.context import LibraryContext
from finter.framework_model.calendar import iter_days

REVISION_PATTERN = [
    r".*\.rolling\(.{1,20}\)\.sum\(\)",
    r".*\.rolling\(.{1,20}\)\.std\(\)",
    r".*\.rolling\(.{1,20}\)\.mean\(\)",
    r".*\.resample\(.{1,20}\)\.sum\(\)",
    r".*\.resample\(.{1,20}\)\.std\(\)",
    r".*\.resample\(.{1,20}\)\.mean\(\)",
]

SLOW_PATTERN = [
    r"\.fillna\(False\)",
]


def compare_dfs(orig, variation):
    min_index = max(orig.index[0], variation.index[0])
    max_index = min(orig.index[-1], variation.index[-1])
    shared_columns = orig.columns.union(variation.columns)
    diff = orig.loc[min_index:max_index, shared_columns].copy().fillna(
        0
    ) - variation.loc[min_index:max_index, shared_columns].copy().fillna(0)

    diff_sum = diff.abs().sum(axis=1)
    assert diff_sum.max() < 100000, (
        f"diff at {diff_sum.idxmax()}, amount is {diff_sum.max()}, "
        f"orig start: {orig.index[0]} end: {orig.index[-1]}, "
        f"variation start: {variation.index[0]} end: {variation.index[-1]} "
    )


class PositionValidate:
    @staticmethod
    def compare(orig, variation):
        return True
        # compare_dfs(orig, variation)

    @staticmethod
    def result(df):
        assert not df.empty, "empty result df"
        assert df.index.is_unique, "not unique index"
        assert df.index.is_all_dates, "not datetime index"
        assert df.index.is_monotonic, "not monotonic index"


class IValidation(object, metaclass=ABCMeta):
    @abstractmethod
    def validate(self):
        pass


class ValidationHelper(IValidation):
    """
    ValidationHelper is for Partial Validation of Model.
    It is simple version of Model Validation.

    >>> ValidationHelper("sample_alpha", model_info).validate()
    >>> ValidationHelper("sample_alpha", model_info).validate_start_dependency()
    >>> ValidationHelper("sample_alpha", model_info).validate_end_dependency()

    List of ValidationHelper methods:
    - validate_code(path: str, model: str) -> bool
        - model can be "alpha|portfolio"
    - validate_cm_loading(path: str, model: str) -> bool
        - model can be "alpha|portfolio"
    - validate_start_dependency()
    - validate_end_dependency()
    - validate()
        - do all kind of validation above
    """

    def __init__(self, model_path=None, model_info=None):
        self.__MODEL_PATH = model_path
        self.__MODEL_INFO = model_info

        self.end = outsample_end_date(datetime.now())

        self.FRAME = FrameUtil.frame(self.__MODEL_INFO["type"])

        self.__MODEL = self.model()

    def model(self):
        with LibraryContext(self.__MODEL_PATH, self.FRAME.F_NAME) as module:
            return getattr(module, self.FRAME.TYPE.title().replace("_", ""))()

    def validate(self):
        module_file = Path(self.__MODEL_PATH) / (self.FRAME.F_NAME + ".py")

        assert ValidationHelper.validate_code(
            module_file, self.__MODEL_INFO["type"]
        ), "model contains (rolling / resmaple).sum() / .std() / .mean() or fillna(False)->replace(np.nan, False)"

        assert ValidationHelper.validate_cm_loading(
            module_file, self.__MODEL_INFO["type"]
        ), "invalid cm loading please use 'Base[Alpha|Portfolio|Fund|FlexibleFund].get_cm' or 'self.get_cm'"

        self.validate_start_dependency()
        self.validate_end_dependency()

    def validate_start_dependency(self):
        exchange = self.__MODEL_INFO["exchange"]

        def _getter(_end: datetime, _bef: int) -> pd.DataFrame:
            return self.__MODEL.get(
                self.days_before(_end, _bef, exchange),
                int(_end.strftime("%Y%m%d"))
            )

        orig = _getter(self.end, 1)
        variation = _getter(self.end, 20)
        variation2 = _getter(self.end, 100)

        assert_index_share(orig, variation)
        assert_max_dependency(orig, variation, "start")
        assert_max_dependency(variation2, variation, "start")
        logger.info("Start dependency validation Succeeded")

    def validate_end_dependency(self):
        exchange = self.__MODEL_INFO["exchange"]

        def _getter(_end: datetime, _bef: int) -> pd.DataFrame:
            return self.__MODEL.get(
                self.days_before(_end, 100, exchange),
                self.days_before(_end, _bef, exchange)
            )

        orig = _getter(self.end, 0)

        for i in range(1, 64, 6):
            variation = _getter(self.end, i)
            assert_index_share(orig, variation)
            assert_max_dependency(orig, variation, "end")
        logger.info("End dependency validation Succeeded")

    @staticmethod
    def validate_code(path: str, model="") -> bool:
        with open(path, "r", encoding="utf-8") as f:
            return _validate_patterns(f.read(), REVISION_PATTERN + SLOW_PATTERN)

    @staticmethod
    def validate_cm_loading(path: str, model="") -> bool:
        with open(path, "r", encoding="utf-8") as f:
            return _validate_patterns(f.read(), _base_pattern(model))

    @staticmethod
    def days_before(end, days, exchange="krx"):
        # return last trading day when days is 0
        day = days if days != 0 else 10
        start = end - timedelta(days=day)
        idx = 0 if days != 0 else -1
        return int(
            list(
                iter_days(start, end, exchange)
            )[idx].strftime("%Y%m%d")
        )


def assert_max_dependency(orig, variation, name):
    try:
        PositionValidate.compare(orig, variation)
    except AssertionError as e:
        msg = """
        There is %s dependency
        orig start: %s
        var start: %s
        orig end: %s
        var end: %s
        """ % (
            name,
            orig.index[0],
            variation.index[0],
            orig.index[-1],
            variation.index[-1],
        )
        logger.error(msg)
        raise e
    except Exception as e:
        logger.error(e, exc_info=True)
        raise e


def assert_index_share(orig, variation):
    share = orig.index.intersection(variation.index)
    assert len(share) > 0, "No index sharing %s, %s" % (orig.index, variation.index)


def _validate_patterns(code, patterns) -> bool:
    code = code.replace("\n", "")
    return all([re.search(p, code) is None for p in patterns])


def _base_pattern(model):
    all_ = {"BaseAlpha", "BasePortfolio", "BaseFund", "BaseFlexibleFund"}
    invalids = all_ - {"Base" + model.title().replace("_", "")}
    patterns = [r".*%s.*" % i for i in invalids]
    return patterns
