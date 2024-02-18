from typing import List
import os,sys
from pnostic.structure import RepoObject, RepoResultObject, SeclusionEnv, SeclusionEnvOutput, Runner


class app(SeclusionEnv):
    def __init__(self):
        super().__init__(working_dir=os.path.abspath(os.curdir))
        self.imports = [
            "ephfile",
            "mystring"
        ]

    def initialize(self) -> bool:
        return True

    def name(self) -> str:
        return "SimpleSeclusion"

    def clean(self) -> bool:
        return True

    def python_packages(self,packages:List[str]) -> bool:
        return True

    def setup_files(self,files:List[str]) -> bool:
        return True

    def process(self, obj:RepoObject, runner:Runner)->SeclusionEnvOutput:
        import ephfile,mystring
        exit_code, exe_logs = -1, []
        startTime,endTime,output="","",[]

        with ephfile.ephfile(contents = obj.content) as eph:
            path_to_scan = None
            if obj.content is None:
                path_to_scan = obj.path
            else:
                path_to_scan = eph()

            try:
                startTime = mystring.current_date()
                output = runner.scan(path_to_scan)
                endTime = mystring.current_date()
                exit_code = 0
            except Exception as e:
                _, _, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                output = [RepoResultObject.newEmpty(
                    projecttype=obj.path,
                    projectname=obj.path,
                    projecturl=None,
                    qual_name=None,
                    tool_name=runner.name(),
                    stage=None,
                    ExceptionMsg="-> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno),
                    startDateTime=None,
                    endDateTime=None
                )]

        return SeclusionEnvOutput(
            start_date_time=startTime,
            scan_object=obj,
            result=output,
            exit_code=exit_code,
            exe_logs="\n".join(exe_logs),
            end_date_time=endTime
        )