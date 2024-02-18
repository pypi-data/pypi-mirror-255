from abc import ABCMeta, abstractmethod

from unstract.sdk.tool.base import BaseTool


class X2Text(metaclass=ABCMeta):
    def __init__(self, tool: BaseTool):
        self.tool = tool

    @abstractmethod
    def convert_to_text(self, input_file: str, basic_convert: bool = False):
        pass
