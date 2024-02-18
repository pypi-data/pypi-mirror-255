import hugg, mystring as mys, os,sys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject

class app(RepoObjectProvider):
    def __init__(self, path:str, extension_regex=None):
        self.path = path
        self.extension_regex = extension_regex

    def initialize(self):
        return True

    def name(self):
        return "Folder Provider"

    def clean(self):
        return True

    @property
    def RepoObjects(self) -> List[RepoObject]:
        for root, dirnames, fnames in os.walk(self.path):
            for fname in fnames:
                relative_path = os.path.join(root, fname)
                full_path = os.path.abspath(relative_path)

                if self.extension_regex is None or self.extension_regex( os.path.splitext(full_path)[-1] ):
                    with open(full_path, "r") as reader:
                        content = mys.string.of("\n".join(reader.readlines()))

                    yield RepoObject(
                        path = relative_path,
                        hash=content.tohash(),
                        content=content,
                        hasVuln=False,cryVulnId=None,langPattern=None,file_scan_lambda=None
                    )