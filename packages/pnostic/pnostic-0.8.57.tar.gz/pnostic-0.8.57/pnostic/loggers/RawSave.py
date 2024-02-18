from typing import Tuple, List, Dict, Union
import mystring, os,sys
from pnostic.structure import Logger, RepoResultObject, RepoObject, RepoSifting
import pnostic.utils as utils

class app(Logger):
    def __init__(self):
        super().__init__()

    def initialize(self) -> bool:
        return True

    def name(self) -> mystring.string:
        return mystring.string.of("Raw Save")

    def clean(self) -> bool:
        return True

    def message(self, msg: str) -> bool:
        return True

    def __relative_pathing(self, path)->str:
        return path.replace(os.path.abspath(os.curdir), "")

    def emergency(self, msg:str)->bool:
        utils.custom_msg(msg, utils.bcolors.FAIL)
        return True

    def __write_out(self, object:RepoObject, second_pathing_argument):
        try:
            file_name = self.file_name(object, second_pathing_argument, suffix=".pkl")

            print("Saving to: {0}".format(file_name))
            object.frame.to_pickle(file_name)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            msg = ":> HIt an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno)
            print(msg)
        return True

    def parameter(self, parameter: RepoObject) -> bool:
        self.__write_out(
            object=parameter,
            second_pathing_argument=self.__relative_pathing(parameter.path).replace("/","_^_")
        )
        return True

    def result(self, result: RepoResultObject) -> bool:
        self.__write_out(
            object=result,
            second_pathing_argument=result.tool_name+"_V_"+self.__relative_pathing(result.qual_name).replace("/","_^_")
        )
        return True
