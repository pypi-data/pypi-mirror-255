from pnostic.structure import Logger, RepoResultObject, RepoObject
import pnostic.utils as utils
import mystring


class app(Logger):
    def __init__(self):
        super().__init__()
        return None

    def initialize(self) -> bool:
        return True

    def name(self) -> mystring.string:
        return mystring.string.of("Print Logger")

    def clean(self) -> bool:
        return True

    def message(self, msg: mystring.string) -> bool:
        print(msg)
        return True

    def emergency(self, msg:str)->bool:
        utils.custom_msg(msg, utils.bcolors.FAIL)
        return True

    def parameter(self, parameter: RepoObject) -> bool:
        print(parameter)
        return True

    def result(self, result: RepoResultObject) -> bool:
        print(result)
        return True
