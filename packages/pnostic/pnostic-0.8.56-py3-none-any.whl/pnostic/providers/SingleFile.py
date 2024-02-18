import mystring as mys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject


class app(RepoObjectProvider):
    def __init__(self, content:str, vulnId:int=-1, langPattern:str=""):
        self.content = mys.string(content)
        self.vulnId = vulnId
        self.hasVuln = self.vulnId is not -1
        self.langPattern = langPattern
        self.path = "stub.py"
        self.file_scan_lambda = None

    def initialize(self) -> bool:
        print("Initializing")
        return True

    def name(self) -> mys.string:
        return mys.string.of("SingleFile Provider")

    def clean(self) -> bool:
        print("Cleaning")
        return True

    @property
    def RepoObjects(self) -> List[RepoObject]:
        yield RepoObject(
            path=self.path,
            hash=self.content.tohash(),
            content=self.content,
            hasVuln=self.hasVuln,
            cryVulnId=self.vulnId,
            langPattern=self.langPattern,
            file_scan_lambda=self.file_scan_lambda
        )
