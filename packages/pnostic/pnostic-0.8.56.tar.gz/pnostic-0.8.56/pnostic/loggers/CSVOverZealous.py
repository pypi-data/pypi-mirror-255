import os, mystring
from typing import List

from pnostic.structure import Logger, RepoResultObject, RepoObject


class app(Logger):
	def __init__(self):
		super().__init__()
		self.set_file_name = None

	def initialize(self) -> bool:
		return True

	def name(self) -> mystring.string:
		return mystring.string.of("OverzealousLogger")

	def clean(self) -> bool:
		return True

	def file_name(self) -> str:
		if self.set_file_name is None:
			ktr,string_file_name = 0, "_stub_csv_base_"

			def filing(name,num):
				return os.path.join(name, str(num)).replace("/","")+".csv"

			while os.path.exists(filing(string_file_name, ktr)):
				ktr +=1 
			self.set_file_name = filing(string_file_name, ktr)

			with open(self.set_file_name, "w+") as writer:
				writer.write("STAGE, MESSAGE\n")

		return self.set_file_name

	def emergency(self, msg:str)->bool:
		try:
			with open(self.name() + "_ERRORS.csv", "a+") as writer:
				writer.write("{0},{1}\n".format("MESSAGE", msg))
			return True
		except Exception as e:
			print(e)
			return False

	def message(self, msg: str) -> bool:
		if True:
			try:
				with open(self.file_name() + "_MSG.csv", "a+") as writer:
					writer.write("{0},{1}\n".format("MESSAGE", msg))
			except Exception as e:
				print(e)
		return True

	def parameter(self, parameter: RepoObject) -> bool:
		try:
			with open(self.file_name(), "a+") as writer:
				writer.write("{0},{1}\n".format("PARAM", parameter.base64JsonString))
		except Exception as e:
			print(e)
		return True

	def result(self, result: RepoResultObject) -> bool:
		try:
			with open(self.file_name(), "a+") as writer:
				writer.write("{0},{1}\n".format("RESULT", result.base64JsonString))
		except Exception as e:
			print(e)
		return True
