from typing import List
import mystring
from pnostic.structure import RepoResultObject, Runner
from multiprocessing import Process

def util_log(string,foil="procedure_log.txt"):
	print(string)
	with open(foil, "a+") as writer:
		writer.write("Openai_API Runner Log:> " + str(string))

def timing():
	print("[",end='',flush=True)
	while True:
		#Created a manual delay
		for _ in range(100_000):
			k=1
		print('.',end='',flush=True)

class app(Runner):
	def __init__(self, openapi_key="", openapi_model="", prefix_for_prompt="",
			frequency_penalty=None, #: Optional[float] | NotGiven = NOT_GIVEN,
			function_call=None, #: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
			functions=None, #: List[completion_create_params.Function] | NotGiven = NOT_GIVEN,
			logit_bias=None, #: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
			logprobs=None, #: Optional[bool] | NotGiven = NOT_GIVEN,
			max_tokens=None, #: Optional[int] | NotGiven = NOT_GIVEN,
			n=None, #: Optional[int] | NotGiven = NOT_GIVEN,
			presence_penalty=None, #: Optional[float] | NotGiven = NOT_GIVEN,
			response_format=None, #: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
			seed=None, #: Optional[int] | NotGiven = NOT_GIVEN,
			stop=None, #: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
			temperature=None, #: Optional[float] | NotGiven = NOT_GIVEN,
			tool_choice=None, #: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
			tools=None, #: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
			top_logprobs=None, #: Optional[int] | NotGiven = NOT_GIVEN,
			top_p=None, #: Optional[float] | NotGiven = NOT_GIVEN,
			fix_response=lambda string:string,
	):
		super().__init__()
		self.openapi_key = openapi_key
		self.openapi_model = openapi_model
		self.prefix_for_prompt = prefix_for_prompt

		#Specific Chatgpt OpenAI Parameters
		self.frequency_penalty = frequency_penalty
		self.function_call = function_call
		self.functions = functions
		self.logit_bias = logit_bias
		self.logprobs = logprobs
		self.max_tokens = max_tokens
		self.n = n
		self.presence_penalty = presence_penalty
		self.response_format = response_format
		self.seed = seed
		self.stop = stop
		self.temperature = temperature
		self.tool_choice = tool_choice
		self.tools = tools
		self.top_logprobs = top_logprobs
		self.top_p = top_p

		#Manual String Patching Method
		self.fix_response = fix_response

		self.imports += [
			"openai==1.10.0", #https://github.com/openai/openai-python
			"tqdm==4.66.1"
		]
		self.client = None

	def initialize(self) -> bool:
		util_log("Initializing")
		try:
			from openai import OpenAI
		except:
			os.system("{sys.executable} -m pip install --upgrade {1}".format(sys.executable, " ".join(self.imports)))
			from openai import OpenAI
		
		try:
			pager = Process(target=timing,args=())
			pager.start()
			self.client = OpenAI(
				api_key=self.openapi_key,
			)
			pager.terminate()
		except Exception as e:
			import os,sys
			exceptionString = str(e)
			_,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			util_log("||>> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))
			util_log(e)
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
			"I'm sorry, but as an AI",
		]:
			for shiftr in [lambda x:x, lambda x:x.lower(), lambda x:x.upper()]:
				if shiftr(string) in shiftr(response):
					return True

		return False

	def __api_wrapped_request(self,messages, model, frequency_penalty, function_call, functions, logit_bias, logprobs, max_tokens, n, presence_penalty, response_format, seed, stop, temperature, tool_choice, tools, top_logprobs, top_p):
		try:
			from openai import OpenAI
		except:
			os.system("{sys.executable} -m pip install --upgrade {1}".format(sys.executable, " ".join(self.imports)))
			from openai import OpenAI
		import openai
		from openai._types import NotGiven
		from tqdm import tqdm

		initial_delay = 1;exponential_base = 2;jitter = True
		max_retries = 20;errors = (openai.RateLimitError,);resp = None
		num_retries = 0;delay = initial_delay;startDateTime = None
		endDateTime = None

		dict_args = {}
		if messages is not None and messages != NotGiven() and not isinstance(messages, NotGiven):
			dict_args["messages"] = messages

		if model is not None and model != NotGiven() and not isinstance(model, NotGiven):
			dict_args["model"] = model

		if frequency_penalty is not None and frequency_penalty != NotGiven() and not isinstance(frequency_penalty, NotGiven):
			dict_args["frequency_penalty"] = frequency_penalty

		if function_call is not None and function_call != NotGiven() and not isinstance(function_call, NotGiven):
			dict_args["function_call"] = function_call

		if functions is not None and functions != NotGiven() and not isinstance(functions, NotGiven):
			dict_args["functions"] = functions

		if logit_bias is not None and logit_bias != NotGiven() and not isinstance(logit_bias, NotGiven):
			dict_args["logit_bias"] = logit_bias

		if logprobs is not None and logprobs != NotGiven() and not isinstance(logprobs, NotGiven):
			dict_args["logprobs"] = logprobs

		if max_tokens is not None and max_tokens != NotGiven() and not isinstance(max_tokens, NotGiven):
			dict_args["max_tokens"] = max_tokens

		if n is not None and n != NotGiven() and not isinstance(n, NotGiven):
			dict_args["n"] = n

		if presence_penalty is not None and presence_penalty != NotGiven() and not isinstance(presence_penalty, NotGiven):
			dict_args["presence_penalty"] = presence_penalty

		if response_format is not None and response_format != NotGiven() and not isinstance(response_format, NotGiven):
			dict_args["response_format"] = response_format

		if seed is not None and seed != NotGiven() and not isinstance(seed, NotGiven):
			dict_args["seed"] = seed

		if stop is not None and stop != NotGiven() and not isinstance(stop, NotGiven):
			dict_args["stop"] = stop

		if temperature is not None and temperature != NotGiven() and not isinstance(temperature, NotGiven):
			dict_args["temperature"] = temperature

		if tool_choice is not None and tool_choice != NotGiven() and not isinstance(tool_choice, NotGiven):
			dict_args["tool_choice"] = tool_choice

		if tools is not None and tools != NotGiven() and not isinstance(tools, NotGiven):
			dict_args["tools"] = tools

		if top_logprobs is not None and top_logprobs != NotGiven() and not isinstance(top_logprobs, NotGiven):
			dict_args["top_logprobs"] = top_logprobs

		if top_p is not None and top_p != NotGiven() and not isinstance(top_p, NotGiven):
			dict_args["top_p"] = top_p


		#Taken From https://platform.openai.com/docs/guides/rate-limits/error-mitigation?context=tier-free
		# Loop until a successful response or max_retries is hit or an exception is raised
		while True:
			try:
				startDateTime = mystring.current_date()
				resp =  self.client.chat.completions.create(**dict_args)
				endDateTime = mystring.current_date()

			# Retry on specific errors
			except errors as e:
				print("Waiting")
				# Increment retries
				num_retries += 1

				# Check if max retries has been reached
				if num_retries > max_retries:
					raise Exception(
						f"Maximum number of retries ({max_retries}) exceeded."
					)

				# Increment the delay
				delay *= exponential_base * (1 + jitter * random.random())

				# Sleep for the delay
				#time.sleep(delay)
				for _ in tqdm(range(delay+1)):
					time.sleep(1)

			# Raise exceptions for any errors not specified
			except Exception as e:
				import os,sys
				exceptionString = str(e)
				_,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				util_log("||>> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))
				util_log(e)

		if resp is not None:
			resp.startDateTime = startDateTime
			resp.endDateTime = endDateTime

		return resp

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
		startDateTime = None
		endDateTime = None
		chat_completion = None
		full_response = None

		try:
			import time
			from tqdm import tqdm
			import openai
			from openai import OpenAI
			from openai._types import NotGiven

			#Setting the extra parameters for OpenAI to NotGiven if None
			self.frequency_penalty = self.frequency_penalty or NotGiven()
			self.function_call = self.function_call or NotGiven()
			self.functions = self.functions or NotGiven()
			self.logit_bias = self.logit_bias or NotGiven()
			self.logprobs = self.logprobs or NotGiven()
			self.max_tokens = self.max_tokens or NotGiven()
			self.n = self.n or NotGiven()
			self.presence_penalty = self.presence_penalty or NotGiven()
			self.response_format = self.response_format or NotGiven()
			self.seed = self.seed or NotGiven()
			self.stop = self.stop or NotGiven()
			self.temperature = self.temperature or NotGiven()
			self.tool_choice = self.tool_choice or NotGiven()
			self.tools = self.tools or NotGiven()
			self.top_logprobs = self.top_logprobs or NotGiven()
			self.top_p = self.top_p or NotGiven()

			while chat_completion is None:
				try:
					startDateTime = mystring.current_date()
					#https://github.com/openai/openai-python/blob/0c1e58d511bd60c4dd47ea8a8c0820dc2d013d1d/src/openai/resources/chat/completions.py#L42
					chat_completion = self.__api_wrapped_request(
						messages=self.prep_messages(user_content),
						model=self.openapi_model,
						#Extra Parameters for OpenAI
						frequency_penalty = self.frequency_penalty,
						function_call = self.function_call,
						functions = self.functions,
						logit_bias = self.logit_bias,
						logprobs = self.logprobs,
						max_tokens = self.max_tokens,
						n = self.n,
						presence_penalty = self.presence_penalty,
						response_format = self.response_format,
						seed = self.seed,
						stop = self.stop,
						temperature = self.temperature,
						tool_choice = self.tool_choice,
						tools = self.tools,
						top_logprobs = self.top_logprobs,
						top_p = self.top_p
					)
					endDateTime = mystring.current_date()
					if chat_completion is None:
						util_log("The chat_completions is None")
						break
					elif self.__api_request_STALLED(chat_completion):
						chat_completion = None
					else:
						#https://github.com/openai/openai-python/blob/0c1e58d511bd60c4dd47ea8a8c0820dc2d013d1d/examples/demo.py#L19
						full_response = str(chat_completion)
						startDateTime = chat_completion.startDateTime
						endDateTime = chat_completion.endDateTime
						chat_completion = chat_completion.choices[0].messages.content
				except openai.APIConnectionError as e:
					util_log("The server could not be reached")
					util_log(e.__cause__)  # an underlying Exception, likely raised within httpx.
					break
				except openai.RateLimitError as e:
					util_log("A 429 status code was received; we should back off a bit.")
					for _ in tqdm(range(60*5)):
						time.sleep(1)
				except openai.APIStatusError as e:
					util_log("Another non-200-range status code was received")
					util_log(e.status_code)
					util_log(e.response)
					break
		except Exception as e:
			import os,sys
			exceptionString = str(e)
			_,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			util_log("||>> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))

		return {
			"CHAT":chat_completion,
			"FULL":full_response,
			"START":startDateTime,
			"STOP":endDateTime,
		}

	def scan(self, filePath: str) -> List[RepoResultObject]:
		try:
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
				startDateTime=str(mystring.now_utc_to_iso()) if startDateTime is None else str(mystring.date_to_iso(startDateTime)),
				endDateTime=str(mystring.now_utc_to_iso()) if endDateTime is None else str(mystring.date_to_iso(endDateTime)),
			)]
		except Exception as e:
			import os,sys
			exceptionString = str(e)
			_,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			util_log("||> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))
			return []

	def name(self) -> mystring.string:
		return mystring.string.of("OpenAPI_{0}".format(self.openapi_model))

	def clean(self) -> bool:
		util_log("Cleaning")
		self.client = None
		return True

	def arg_init_string(self)->str:
		return ""