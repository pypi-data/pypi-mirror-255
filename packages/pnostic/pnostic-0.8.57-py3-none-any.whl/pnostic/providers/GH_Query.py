import hugg, mystring as mys, os,sys
from typing import List

from pnostic.structure import RepoObjectProvider, RepoObject


class app(RepoObjectProvider):
	"""
	https://github.com/search/advanced
	https://pygithub.readthedocs.io/en/stable/examples/MainClass.html#search-repositories-by-language

	https://pygithub.readthedocs.io/en/stable/examples/MainClass.html#search-repositories-by-language

	https://www.freecodecamp.org/news/github-search-tips/
	https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#constructing-a-search-query
	https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories

	https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax

	#####https://github.com/search/advanced
	"""
	def __init__(self, token: str, query:str=None, start_num:int=-1,end_num:int=-1):
		self.token = token
		self.query = query
		self.query_bot = None

		self.start_num = start_num
		self.end_num = end_num
	"""
	queries 
	
	"""

	def initialize(self) -> bool:
		try:
			#https://pygithub.readthedocs.io/en/latest/github.html#github.MainClass.Github.search_repositories
			self.query_bot = hugg.q_ghub(token=self.token, query_string=self.query, start_num = self.start_num, end_num = self.end_num)
			return True
		except Exception as e:
			print(e)
			return False

	def name(self) -> mys.string:
		return mys.string.of("GH Query Provider")

	def clean(self) -> bool:
		return True

	@property
	def repos(self):
		for repo in self.query_bot.repos:
			yield repo

	@property
	def RepoObjects(self) -> List[RepoObject]:
		for repo in self.repos:
			for foil in repo:
				repo.download(foil, os.path.basename(foil))

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
