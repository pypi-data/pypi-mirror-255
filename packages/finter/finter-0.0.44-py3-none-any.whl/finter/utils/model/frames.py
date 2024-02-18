from typing import Type, List
from abc import ABCMeta, abstractmethod


class IFrame(metaclass=ABCMeta):
    @property
    @abstractmethod
    def TYPE(self) -> str:
        pass

    @property
    @abstractmethod
    def IDENTITY_STRUCTURE(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def F_NAME(self) -> str:
        pass


class AlphaFrame(IFrame):
    TYPE = "alpha"
    IDENTITY_STRUCTURE = [
        "type",
        "exchange",
        "universe",
        "instrument_type",
        "author",
        "nickname",
    ]
    F_NAME = "am"


class PortfolioFrame(IFrame):
    TYPE = "portfolio"
    IDENTITY_STRUCTURE = [
        "type",
        "exchange",
        "universe",
        "instrument_type",
        "author",
        "nickname",
    ]
    F_NAME = "pf"


class FrameUtil:
    @classmethod
    def frame(cls, model_type) -> Type[IFrame]:
        if model_type == "alpha":
            return AlphaFrame
        elif model_type == "portfolio":
            return PortfolioFrame
        else:
            raise ValueError("Invalid Frame")
