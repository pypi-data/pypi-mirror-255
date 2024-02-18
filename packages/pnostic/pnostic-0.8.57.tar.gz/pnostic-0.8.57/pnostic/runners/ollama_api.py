from typing import List
import mystring
from pnostic.structure import RepoResultObject, Runner

class app(Runner):
	def __init__(self, host=None, model="llama2", prefix_for_prompt="",fix_response=lambda string:string,	  
		num_keep=None,
		seed=None,
		num_predict=None,
		top_k=None,
		top_p=None,
		tfs_z=None,
		typical_p=None,
		repeat_last_n=None,
		temperature=None,
		repeat_penalty=None,
		presence_penalty=None,
		frequency_penalty=None,
		mirostat=None,
		mirostat_tau=None,
		mirostat_eta=None,
		penalize_newline=None,
	):
		super().__init__()
		self.host = host
		self.model = model
		self.prefix_for_prompt = prefix_for_prompt

		#Manual String Patching Method
		self.fix_response = fix_response

		#Extra runtime options
		self.num_keep = num_keep
		self.seed = seed
		self.num_predict = num_predict
		self.top_k = top_k
		self.top_p = top_p
		self.tfs_z = tfs_z
		self.typical_p = typical_p
		self.repeat_last_n = repeat_last_n
		self.temperature = temperature
		self.repeat_penalty = repeat_penalty
		self.presence_penalty = presence_penalty
		self.frequency_penalty = frequency_penalty
		self.mirostat = mirostat
		self.mirostat_tau = mirostat_tau
		self.mirostat_eta = mirostat_eta
		self.penalize_newline = penalize_newline

		self.imports += [
			"ollama==0.1.4", #https://github.com/ollama/ollama/tree/main
			"tqdm==4.66.1",
			"backoff==2.2.1"
		]
		self.client = None

	def initialize(self) -> bool:
		print("Initializing")
		return True

	@staticmethod
	def __api_request_STALLED(response):
		for string in [
			"I couldn't complete your request.",
			"Rephrase your prompt",
			"outside of my capabilities",
			"I'm unable to help",
			"I can't help you with that",
			"I'm unable to",
		]:
			if string in response:
				return True

		return False

	def prep_messages(self, source_code):
		messages = []
		if self.prefix_for_prompt:
			messages += [{
				"role": "system",
				"content": self.prefix_for_prompt,
			}]

		messages += [{
			"role":"user",
			"content":"SOURCE="+self.fix_response(mystring.string.of(source_code).noNewLine(";"))
		}]

		return messages

	def __api_request(self,user_content):
		import time
		from tqdm import tqdm

		startDateTime = None
		endDateTime = None
		chat_completion = None
		full_response = None

		try:
			from ollama import Client
		except:
			os.system("{sys.executable} -m pip install --upgrade {1}".format(sys.executable, " ".join(self.imports)))

		while chat_completion is None:
			try:
				#https://github.com/openai/openai-python/blob/0c1e58d511bd60c4dd47ea8a8c0820dc2d013d1d/src/openai/resources/chat/completions.py#L42
				core = None
				if self.host:
					from ollama import Client
					client = Client(host=self.host)
					core = client
				else:
					import ollama
					core = ollama

				chat_completion = core.chat(
					model=self.openapi_model,
					messages=self.prep_messages(user_content),	
					num_keep=self.num_keep,
					seed=self.seed,
					num_predict=self.num_predict,
					top_k=self.top_k,
					top_p=self.top_p,
					tfs_z=self.tfs_z,
					typical_p=self.typical_p,
					repeat_last_n=self.repeat_last_n,
					temperature=self.temperature,
					repeat_penalty=self.repeat_penalty,
					presence_penalty=self.presence_penalty,
					frequency_penalty=self.frequency_penalty,
					mirostat=self.mirostat,
					mirostat_tau=self.mirostat_tau,
					mirostat_eta=self.mirostat_eta,
					penalize_newline=self.penalize_newline,
				)

				if self.__api_request_STALLED(chat_completion):
					chat_completion = None
				else:
					#https://github.com/openai/openai-python/blob/0c1e58d511bd60c4dd47ea8a8c0820dc2d013d1d/examples/demo.py#L19
					full_response = str(chat_completion)
					startDateTime = chat_completion.startDateTime
					endDateTime = chat_completion.endDateTime
					chat_completion = chat_completion["message"]["content"]
			except Exception as e:
				print("The server could not be reached")
				print(e.__cause__)  # an underlying Exception, likely raised within httpx.
				break

		return {
			"CHAT":chat_completion,
			"FULL":full_response,
			"START":startDateTime,
			"STOP":endDateTime,
		}

	def scan(self, filePath: str) -> List[RepoResultObject]:
		import json

		with open(filePath, "r") as reader:
			content = '\n'.join(reader.readlines())

		chat_and_full = self.__api_request("")
		chat,raw,startDateTime,endDateTime = chat_and_full["CHAT"],chat_and_full["FULL"],chat_and_full["START"],chat_and_full["STOP"]

		return [RepoResultObject(
			projecttype="",
			projectname=self.name(),
			projecturl="",
			qual_name="",
			tool_name=self.name(),
			Program_Lines=-1,
			Total_Lines=content.count("\n"),
			Number_of_Imports=-1,
			MCC=-1,
			IsVuln=None,
			ruleID=None,
			cryptolationID=-1,
			CWEId=None,
			Message=mystring.obj_to_string(raw, prefix="json:").tobase64(prefix="b64:"),
			Exception=None,
			llmPrompt=mystring.string.of(
				self.prep_messages(content)
			).tobase64(prefix="b64:"),
			llmResponse=mystring.string.of(chat).tobase64(prefix="b64:"),
			extraToolInfo="",
			fileContent=mystring.string.of(content).tobase64(prefix="b64:"),
			Line=-1,
			correctedCode=None,
			severity="",
			confidence="",
			context="",
			TP=0,
			FP=0,
			TN=0,
			FN=0,
			dateTimeFormat="ISO",
			startDateTime=str(mystring.date_to_iso(startDateTime)),
			endDateTime=str(mystring.date_to_iso(endDateTime)),
		)]

	def name(self) -> mystring.string:
		return mystring.string.of("ollama_{0}".format(self.model))

	def clean(self) -> bool:
		print("Cleaning")
		return True

	def arg_init_string(self)->str:
		return ""