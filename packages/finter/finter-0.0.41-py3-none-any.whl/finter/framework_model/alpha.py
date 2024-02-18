from abc import ABCMeta, abstractmethod
from finter.framework_model import ContentModelLoader


class BaseAlpha(metaclass=ABCMeta):
    __CM_LOADER = ContentModelLoader()
    __cm_set = set()

    @abstractmethod
    def get(self, start, end):
        pass

    @classmethod
    def get_cm(cls, key):
        if key.startswith("content."):
            cls.__cm_set.add(key)
        else:
            cls.__cm_set.add('content.' + key)
        return cls.__CM_LOADER.load(key)

    def depends(self):
        return self.__cm_set
