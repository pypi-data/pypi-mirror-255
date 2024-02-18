import hugg, mystring as mys, os,sys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject


class app(RepoObjectProvider):
	def __init__(self, repo:str, token: str, branch_commitsha:str="master", usewget=False):
		self.token = token
		self.repo = hugg.ghub(repo=repo, access_token=token, branch_commitsha=branch_commitsha, usewget=usewget)

	def initialize(self) -> bool:
		return True

	def name(self) -> mys.string:
		return mys.string.of("GH Single Repo Provider")

	def clean(self) -> bool:
		return True

	@property
	def RepoObjects(self) -> List[RepoObject]:
		for file in self.repo.files:
			self.repo.download(foil, os.path.basename(foil))

			with open(os.path.basename(foil), "r") as reader:
				content = "\n".join(reader.readlines)

			yield RepoObject(
				path=os.path.basename(foil),
				hash=None,
				content=content,
				hasVuln=False,
				cryVulnId=None,
				langPattern=None,
				file_scan_lambda=None
			)
