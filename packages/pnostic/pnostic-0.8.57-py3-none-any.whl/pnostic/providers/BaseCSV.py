import hugg, mystring as mys, os,sys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject

class app(RepoObjectProvider):
    def __init__(self, path, file_name_column:str="FileName", file_content_column:str="Contents"):
        self.path = path
        self.data = None
        self.imports = ["pandas", "mystring[all]"]
        self.file_name_column = file_name_column
        self.file_content_column = file_content_column

    def initialize(self):
        import pandas as pd, mystring as mys
        self.data = mys.frame(pd.read_csv(self.path))
        return True

    def name(self):
        return "Custom CSV"

    def clean(self):
        return True

    @property
    def RepoObjects(self) -> List[RepoObject]:
        if self.data is None:
            self.initialize()
        import mystring as mys

        for row in self.data.roll:
            content = mys.string.of(row[self.file_content_column])

            yield RepoObject(
                path = row[self.file_name_column],
                hash=content.tohash(),
                content=content,
                hasVuln=False,cryVulnId=None,langPattern=None,file_scan_lambda=None
            )