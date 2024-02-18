import hugg, mystring as mys, os, sys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject


class app(RepoObjectProvider):
    def __init__(self, hugg_repo:hugg.mem):
        self.hugg_repo = hugg_repo

    def initialize(self) -> bool:
        print("Initializing")
        return True

    def name(self) -> str:
        return "Generic Hugg Provider for {0}".format(self.hugg_repo.__class__.__name__)

    def clean(self) -> bool:
        print("Cleaning")
        return True

    @property
    def RepoObjects(self) -> List[RepoObject]:
        for hugg_foil in self.hugg_repo.files():
            content = mys.string.of(self.hugg_repo.load_text(hugg_foil))

            yield RepoObject(
                path=hugg_foil,
                hash=content.tohash(),
                content=content,
                hasVuln=False,
                cryVulnId=None,
                langPattern=None,
                file_scan_lambda=None,
            )
