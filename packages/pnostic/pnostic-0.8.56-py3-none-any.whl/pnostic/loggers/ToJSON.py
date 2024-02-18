import os, mystring
from typing import List

from pnostic.structure import Logger, RepoResultObject, RepoObject
import pnostic.utils as utils

class app(Logger):
    def __init__(self):
        super().__init__()

    def initialize(self) -> bool:
        return True

    def name(self) -> mystring.string:
        return mystring.string.of("JSON Logger")

    def clean(self) -> bool:
        return True

    def message(self, msg: mystring.string) -> bool:
        return True

    def emergency(self, msg:str)->bool:
        utils.custom_msg(msg, utils.bcolors.FAIL)
        return True

    def parameter(self, parameter: RepoObject) -> bool:
        return True

    def result(self, result: RepoResultObject) -> bool:
        try:
            file_name: mystring.string = self.file_name(result, extraString=result.tool_name, suffix=".json", newFile=False)
            existed = os.path.exists(file_name)
            with open(file_name, "a+" if existed else "w+") as writer:
                if not existed:
                    writer.write("[\n")
                writer.write(mystring.string.of(result.jsonString).replace("\n", "")+"\n,")
            return True
        except Exception as e:
            print(e)
            return False
