# coding:utf8
from typing import Any, Optional, Sequence, Tuple, Union, AnyStr, Mapping
from enum import Enum
import warnings

Numeric = Union[int, float]
MoreOption = Optional[Mapping]


class BasicOptsMetaClass(type):

    def __init__(self, cls, inherit, attributes):
        if len(inherit) == 0 or (cls != 'BasicOpts' and BasicOpts not in inherit):
            warnings.warn(f"{cls} Must inherit the BasicOpts!")

    def __call__(self, *args, **kwargs):
        if args:
            warnings.warn(f"must use keyword argument for OptionCls")
        obj = object.__new__(self)
        obj.__dict__['options'] = {}
        for k, v in kwargs.items():
            """
            Some keyword and python conflict, you can use the beginning of the underline to solve, but we will warn
            """

            if k[0] == '_':
                warnings.warn(f"argument best not to start with an underline,because we will remove the underline")
                k=k[1:]
            if v.__class__ in BasicOpts.__subclasses__():
                obj.__dict__['options'][k] = v.getOpt()
                continue
            obj.__dict__['options'][k] = v
        self.__init__(obj, *args, **kwargs)
        return obj


class BasicOpts(object, metaclass=BasicOptsMetaClass):
    __slots__: ("options",)

    def updOpt(self, **kwargs):
        self.options.update(kwargs)

    def getOpt(self, key: str = None) -> Any:
        if not key:
            return self.options
        return self.options.get(key)

    def setOpt(self, kwargs):
        """
        这里会进行opt类参数默认值的填充
        :param kwargs:
        :return:
        """
        for k, v in kwargs.items():
            if self == v or k == 'kwargs':
                continue
            if v.__class__ in BasicOpts.__subclasses__():
                self.options[k] = v.getOpt()
                continue
            self.options[k] = v


class SnaplineOptions(BasicOpts):
    def __init__(self,
                 className: Optional[str] = "undefined",
                 tolerance: Optional[Numeric] = 10,
                 sharp: Optional[bool] = False,
                 resizing: Optional[bool] = False,
                 clean: Union[Numeric, bool] = False,
                 **kwargs
                 ):
        self.setOpt(locals())


class BackgroundOptions(BasicOpts):
    def __init__(self,
                 color: Optional[str] = "#fffbe6",
                 image: Optional[str] = "undefined",
                 position: Optional[str] = "center",
                 size: Optional[str] = "auto auto",
                 repeat: Optional[str] = "no-repeat",
                 opacity: Optional[Numeric] = 1,
                 quality: Optional[Numeric] = 1,
                 angle: Optional[Numeric] = 20,
                 **kwargs
                 ):
        self.setOpt(locals())


class Args(BasicOpts):
    def __init__(self, **kwargs):
        self.setOpt(locals())


class GridOptions(BasicOpts):
    def __init__(self,
                 type: Optional[str] = "dot",
                 size: Optional[Numeric] = 10,
                 visible: Optional[bool] = True,
                 color: Optional[str] = "#AAAAAA",
                 thickness: Optional[Numeric] = 1.0,
                 **kwargs
                 ):
        arg = Args(thickness=thickness, color=color)
        self.setOpt(locals())


if __name__ == '__main__':
    x = BackgroundOptions()
    print(x.getOpt())

    x = GridOptions()
    print(x.getOpt())

    y = SnaplineOptions(className='1', _sync=x)
    print(y.getOpt())
