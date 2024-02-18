from typing import List, Dict, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import mystring, uuid, threading, os, sys, splych, datetime, threading, asyncio, time
try: #Python2
    import __builtin__ as builtins
except:
    import builtins

class RepoSifting(object):
    def __init__(self):
        self.uuid = ""
        self.stage = None
        self.startDateTime = ""
        self.endDateTime = ""

    def staticKeyTypeMap(self) -> Dict[str, type]:
        return {
            **{
                "uuid": mystring.string,
                "stage": mystring.string,
            },
            **self._internal_staticKeyTypeMap()
        }

    def __setattr__(self, variable_name, variable_value):
        if variable_name in ["startDateTime","endDateTime"] and isinstance(variable_value, datetime.datetime):
            super().__setattr__(variable_name, str(mystring.date_to_iso(variable_value)))
        else:
            super().__setattr__(variable_name, variable_value)

    def __getstate__(self):
        import inspect
        #https://realpython.com/python-pickle-module/
        # Used for creating a pickle
        new_attributes = {
            "__reconvert__":[]
        }

        for key, value in self.__dict__.copy().items():
            if isinstance(value, datetime.datetime):
                new_attributes[key] = value.isoformat()
                new_attributes["__reconvert__"] += [key]
            elif key == "file_scan_lambda":
                new_attributes[key] = inspect.getsource(value)
                new_attributes["__reconvert__"] += [key]
            else:
                new_attributes[key] = value 

        return new_attributes

    def __setstate__(self, state):
        #https://realpython.com/python-pickle-module/
        # Used for loading a pickle
        self.__dict__ = {}
        for key, value in state.items():
            if key in state["__reconvert__"]:
                try:
                    if key == "file_scan_lambda":
                        self.__dict__[key] = eval(value)
                    elif key in ["startDateTime","endDateTime"]:
                        self.__dict__[key] = datetime.datetime.fromisoformat(value)
                except:
                    self.__dict__[key] = value
                    pass
            else:
                self.__dict__[key] = value

    @staticmethod
    @abstractmethod
    def _internal_staticKeyTypeMap() -> Dict[str, type]:
        pass

    def toMap(self) -> Dict[str, Union[str, int, bool]]:
        #https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
        #return {a:getattr(self,a) for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))}
        output:Dict[str, Union[str, int, bool]] = {}
        for key in self.staticKeyTypeMap().keys():
            output[key] = getattr(self,key)
        return output

    @property
    def frame(self):
        return mystring.frame.from_arr([self.toMap()])

    @property
    def jsonString(self):
        import json
        return json.dumps(self.toMap())

    @property
    def base64JsonString(self):
        import json
        return mystring.string.of(json.dumps(self.toMap())).tobase64(prefix=True)

    @property
    def csvString(self):
        #https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
        import csv,io
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(self.toMap().values())
        return output.getvalue()
    
    @property
    def csvHeader(self):
        #https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
        import csv,io
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(self.staticKeyTypeMap.keys())
        return output.getvalue()

    @property
    def csvStrings(self):
        #https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
        import csv,io
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        for value in self.toMap().values():
            writer.writerow(value)
        return output.getvalue()

class RepoObject(RepoSifting):
    def __init__(self, path: mystring.string, hash: mystring.string, content: mystring.string, hasVuln: bool, cryVulnId: int, langPattern: mystring.string = None, file_scan_lambda: mystring.string = None):
        super().__init__()
        self.path = path
        self.file_scan_lambda = file_scan_lambda
        self.hash = hash
        self._content = content
        self.hasVuln = hasVuln
        self.cryVulnId = cryVulnId
        self.langPattern = langPattern

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    def str_type(self):
        return "dir" if self.is_dir else "file"

    @staticmethod
    def _internal_staticKeyTypeMap() -> Dict[str, type]:
        return {
            "path": mystring.string,
            "hash": mystring.string,
            "_content": mystring.string,
            "hasVuln": bool,
            "cryVulnId": int,
            "langPattern": mystring.string,
            "file_scan_lambda": Callable
        }

    def updateContent(self, newContent:mystring.string):
        self._content = newContent
        return self._content

    @property
    def content(self):
        return self._content
    
    @property
    def contentb64(self):
        return self._content.tobase64()

class RepoResultObject(RepoSifting):
    def __init__(self, projecttype: str, projectname: str, projecturl: str, qual_name: str, tool_name: str, Program_Lines: int, Total_Lines: int, Number_of_Imports: int, MCC: int, IsVuln: bool, ruleID: int, cryptolationID: int, CWEId: int, Message: str, Exception:str, llmPrompt:str, llmResponse:str, extraToolInfo:str, fileContent:str, Line: int, correctedCode:str, severity: str=None, confidence: str=None, context: str=None, TP: int=0, FP: int=0, TN: int=0, FN: int=0, dateTimeFormat:str="ISO 8601", startDateTime:str=None, endDateTime:str=None, stage:str=None):
        super().__init__()
        self.projecttype = projecttype
        self.projectname = projectname
        self.projecturl = projecturl

        self.qual_name = qual_name
        self.tool_name = tool_name

        self.Program_Lines = Program_Lines
        self.Total_Lines = Total_Lines
        self.Number_of_Imports = Number_of_Imports
        self.MCC = MCC
        self.fileContent = fileContent

        self.IsVuln = IsVuln
        self.ruleID = ruleID
        self.cryptolationID = cryptolationID
        self.CWEId =  CWEId
        self.Message = Message
        self.Line = Line
        self.correctedCode = correctedCode
        self.severity = severity
        self.confidence = confidence
        self.context = context

        self.Exception = Exception
        self.extraToolInfo = extraToolInfo

        self.llmPrompt = llmPrompt
        self.llmResponse = llmResponse
        self.TP = TP
        self.FP = FP
        self.TN = TN
        self.FN = FN

        self.dateTimeFormat=dateTimeFormat
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime
        self.stage = stage

    @staticmethod
    def newEmpty(projecttype: str,projectname: str,projecturl: str,qual_name: str,tool_name: str,ExceptionMsg:str=None,stage:str=None,startDateTime:str=None,endDateTime:str=None):
        return RepoResultObject(
            projecttype=projecttype,
            projectname=projectname,
            projecturl=projecturl,
            qual_name=qual_name,
            tool_name=tool_name,
            Program_Lines=None,
            Total_Lines=None,
            Number_of_Imports=None,
            MCC=None,
            IsVuln=False,
            ruleID=None,
            cryptolationID=None,
            CWEId=None,
            Message=None,
            Exception=ExceptionMsg,
            llmPrompt=None,
            llmResponse=None,
            extraToolInfo=None,
            fileContent=None,
            Line=None,
            correctedCode=None,
            severity=None,
            confidence=None,
            context=None,
            TP=0,
            FP=0,
            TN=0,
            FN=0,
            dateTimeFormat="ISO 8601",
            startDateTime=startDateTime,
            endDateTime=endDateTime,
            stage=stage
        )

    @staticmethod
    def _internal_staticKeyTypeMap() -> Dict[str, type]:
        return {
            "projecttype": str,
            "projectname": str,
            "projecturl": str,
            "qual_name": str,
            "tool_name": str,
            "Program_Lines": int,
            "Total_Lines": int,
            "Number_of_Imports": int,
            "MCC": int,
            "IsVuln": bool,
            "ruleID": int,
            "cryptolationID": int,
            "CWEId": int,
            "Message": str,
            "Exception":str,
            "llmPrompt":str,
            "llmResponse":str,
            "extraToolInfo":str,
            "fileContent":str,
            "Line": int,
            "correctedCode":str,
            "severity": str,
            "confidence": str,
            "context": str,
            "TP": int,
            "FP": int,
            "TN": int,
            "FN": int,
            "dateTimeFormat":str,
            "startDateTime":str,
            "endDateTime":str,
            "stage":str
        };

    @staticmethod
    def fromCSVLine(line:mystring.string) -> Union[any,None]:
        numAttributes:int = len(RepoResultObject.staticKeyTypeMap().keys())
        splitLine:List[str] = [x.strip() for x in line.split(",")]

        if len(splitLine) != numAttributes:
            return None

        info:Dict[str, any] = {}
        for keyitr,key,value in enumerate(RepoResultObject.staticKeyTypeMap().items()):
            info[key] = getattr(builtins,value)(splitLine[keyitr])

        return RepoResultObject(**info)

class CoreObject(ABC):
    def __init__(self):
        self.imports = []
        self.logger_set = None
        import sys;self.executable = sys.executable

    def set_logger_set(self, logger_set):
        self.logger_set = logger_set

    def installImports(self) -> bool:
        if not hasattr(self, "imports"):
            setattr(self, "imports", [])

        cmd = mystring.string.of("{0} -m pip install {1}".format(sys.executable, ' '.join(self.imports)))
        try:
            if len(self.imports) > 0:
                cmd.exec()
            return True
        except:
            return False

    @abstractmethod
    def initialize(self)->bool:
        pass

    @abstractmethod
    def name(self) -> mystring.string:
        pass

    @abstractmethod
    def clean(self) -> bool:
        pass

class Runner(CoreObject):
    @abstractmethod
    def scan(self,filePath: str) -> List[RepoResultObject]:
        pass

    @abstractmethod
    def arg_init_string(self)->str:
        pass

class Envelop(CoreObject):
    @abstractmethod
    def per_next_repo_obj(self,repo_object: RepoObject):
        pass

    @abstractmethod
    def per_repo_obj_scan(self,repo_object: RepoObject, runner:Runner):
        pass

    @abstractmethod
    def per_repo_obj_scan_result(self,repo_object: RepoResultObject, runner:Runner):
        pass

class EnvelopSet(object):
    def __init__(self, envelops=[]):
        self.envelops = envelops

    def __len__(self):
        return len(self.envelops)

    def add(self, envelop:Envelop):
        envelop.initialize()
        self.envelops += [envelop]

    def per_next_repo_obj(self,repo_object: RepoObject):
        for envelop in self.envelops:
            try:
                envelop.per_next_repo_obj(repo_object)
            except:pass

    def per_repo_obj_scan(self,repo_object: RepoObject, runner:Runner):
        for envelop in self.envelops:
            try:
                envelop.per_repo_obj_scan(repo_object, runner)
            except:pass

    def per_repo_obj_scan_result(self,repo_object: RepoResultObject, runner:Runner):
        for envelop in self.envelops:
            try:
                envelop.per_repo_obj_scan_result(repo_object, runner)
            except:pass

class Logger(CoreObject):
    def __init__(self):
        super().__init__()
        self.stage:mystring.string = None
        self.general_prefix = None

    @abstractmethod
    def message(self, msg:mystring.string)->bool:
        pass

    @abstractmethod
    def emergency(self, msg:mystring.string)->bool:
        pass

    @abstractmethod
    def parameter(self,parameter:RepoObject)->bool:
        pass

    @abstractmethod
    def result(self,result:RepoResultObject)->bool:
        pass

    def file_size_limit_bytes(self)->float:
        return float('inf')

    def break_file_down(self, file_path:str)->List[str]:
        file_size = os.path.getsize(file_path)
        if file_size < self.file_size_limit_bytes():
            return [file_path]


        if not file_path.endswith(".zip"):
            import hugg
            zyp_container = hugg.zyp(file_path+".zip")
            zyp_container[file_path] = file_path
            file_path = zyp_container.location
        
        return splych.file_split(file_path, chunk_size=self.file_size_limit_bytes, delete_original=True)

    def __relative_pathing(self, path)->str:
        return path.replace(os.path.abspath(os.curdir), "")

    def file_name(self, result:RepoSifting, extraString:str='', prefix:str='', suffix:str=".txt", newFile:bool=True)->str:
        current_file = mystring.string.of("{0}_{1}/{2}_{3}".format(
            prefix,
            result.uuid,
            extraString,
            suffix
        ))
        if self.general_prefix:
            current_file = self.__relative_pathing(mystring.string.of("{0}_{1}".format(self.general_prefix, current_file)))

        if newFile:
            ktr = 0
            while os.path.exists(current_file):
                current_file = current_file.replace(suffix, "_{0}{1}".format(ktr, suffix))
                ktr += 1
        os.makedirs(os.path.dirname(current_file), exist_ok=True)
        return current_file

    def start(self, stage:mystring.string):
        self.stage = stage
        self.send("01: Entering the stage: {0}".format(self.stage))
        return self

    def send(self, msg:Union[mystring.string, RepoObject, RepoResultObject])->bool:
        successful = True
        try:
            if isinstance(msg, RepoResultObject):
                self.result(msg)
            elif isinstance(msg, RepoObject):
                self.parameter(msg)
            else: #if isinstance(msg, mystring.string):
                self.message(msg)
        except Exception as e:
            successful = False
        return successful

    def stop(self):
        self.send("02: Exiting the stage: {0}".format(self.stage))
        return self

class LoggerSet(object):
    def __init__(self, loggers=[], stage:str=None,log_debug_messages=False, logger_queue_lock=threading.Lock()):
        self.loggers = loggers
        self.stage = stage
        self.log_debug_messages = log_debug_messages
        self.logger_queue_lock = logger_queue_lock

    def __len__(self):
        return len(self.loggers)

    def add(self, logger:Logger):
        self.loggers += [logger]

    def set_prefix(self, general_prefix:mystring.string):
        for logger in self.loggers:
            with self.logger_queue_lock:
                logger.general_prefix = general_prefix
        return self

    def start(self, stage:mystring.string):
        for logger in self.loggers:
            with self.logger_queue_lock:
                if self.log_debug_messages:logger.send("03: sending to logger {0}".format(logger.name()))
                logger.start(self.stage or stage)
                if self.log_debug_messages:logger.send("04: ^^^^^ sending to {0}".format(logger.name()))
        return self

    def send(self, msg:Union[mystring.string, RepoObject, RepoResultObject])->bool:
        for logger in self.loggers:
            with self.logger_queue_lock:
                if self.log_debug_messages:logger.send("05: sending to {0}".format(logger.name()))
                logger.send(msg)
                if self.log_debug_messages:logger.send("06: end sending to {0}".format(logger.name()))
        return self

    def emergency(self, msg:mystring.string)->bool:
        for logger in self.loggers:
            with self.logger_queue_lock:
                logger.emergency(msg)

    def stop(self):
        for logger in self.loggers:
            with self.logger_queue_lock:
                if self.log_debug_messages:logger.send("07: sending to {0}".format(logger.name()))
                logger.stop()
                if self.log_debug_messages:logger.send("08: end sending to {0}".format(logger.name()))
        return self

    def __enter__(self, stage:Union[mystring.string, None]=None):
        stage = self.stage or stage
        self.start(stage=stage)
        return self

    def __exit__(self, _type=None, value=None, traceback=None):
        self.stop()

class RepoObjectProvider(CoreObject):
    @property
    @abstractmethod
    def RepoObjects(self) -> List[RepoObject]:
        pass

@dataclass
class SeclusionEnvOutput:
    start_date_time:str
    scan_object:RepoObject
    result:List[RepoResultObject]
    exit_code:int
    exe_logs:str
    end_date_time:str

class SeclusionEnv(CoreObject):
    def __init__(self, working_dir:str, user:str="root"):
        super().__init__()
        self.working_dir = working_dir
        self.user = user

    @abstractmethod
    def python_packages(self,packages:List[str]) -> bool:
        pass

    @abstractmethod
    def setup_files(self,files:List[str]) -> bool:
        pass

    @abstractmethod
    def process(self, obj:RepoObject, runner:Runner)->SeclusionEnvOutput:
        pass

class contextString(object):
    def __init__(self, lines=List[str], vulnerableLine:str=None, imports:List[str] = []):
        self.lines:List[str] = lines
        self.vulnerableLine:str = vulnerableLine
        self.imports = imports

    @staticmethod
    def fromString(context:str) -> any:
        lines:List[str] = []
        vulnerableLine:str = None
        imports:List[str] = []

        for line in context.split("\n"):
            #001:       println("1")
            #002:       println("1") #!
            num:int = line.split(":")[0]
            content:str = line.split(":")[1]
            vulnerable:bool = content.endswith("#!")

            if vulnerable and vulnerableLine is None:
                vulnerableLine = content

            rawcontent:str = content.replace(line.strip(),'')
            whitespace:str = content.replace(rawcontent,'')
            isImport:bool = "import" in rawcontent
            if isImport:
                imports += [rawcontent]

            lines += [{
                "RawLine":line,
                "LineNum":num,
                "RawContent":rawcontent,
                "IsVulnerable":vulnerable,
                "Whitespace":whitespace,
                "IsImport":isImport
            }]
        
        return contextString(lines=lines, vulnerableLine=vulnerableLine, imports=imports)

    def toString(self) -> str:
        output = []

        for line in self.lines:
            output += "#{0}:{1}{2} {3}".format(
                line['LineNum'],
                line['Whitespace'],
                line['RawContent'],
                '#!' if line['IsVulnerable'] else ''
            )

        return '\n'.join(output)

def set_time_wrapper(date_time):
    output = ""
    if date_time is not None:
        output = date_time
        try:
            output = str(mystring.date_to_iso(date_time))
        except:pass
    return output

class ThreadWithReturnValue(threading.Thread):
    #https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return


class GenProcedure(ABC):
    """_summary_

    Args:
        ABC (_type_): _description_

with utils.clean_op_env():
	class operation(structure.GenProcedure):
		def __init__(self):
			super().__init__(
				fileProviders = [
					SingleFile.app(content="import os,sys;print('Hello World')")
				],
				runners = [
					simple.app(),
				],
				loggersset = [
					Printr.app(),
				],
				enveloperset = [
					LiveGraph.app(ipaddress='0.0.0.0', port_to_use=5000)
				],
				perScan = None, # A Lambda to run after each scan
				general_prefix = None, # A prefix to add within the objects and results
				log_debug_messages = False, # Log debug messages
				use_results = False, # Use the results from the runner within the run procedure method
				thread_count = 1, # The number of threads to use
				seclusion_env = core_seclusion, # The seclusion environment to use, by default it's simply the current python environment
				seclusion_env_necessary_files = [] # The files to include in the seclusion environment
			)

		def run_procedure(self):
			with structure.LoggerSet(loggers=self.loggerSet.loggers, stage="StageOne") as logggg:
				for runnerSvr in self.runners:
					with self.getRunnerProcedure(runnerSvr) as runner:
						for fileObj in self.RepoObjects:
							firstScanResults: List[RepoResultObject] = self.process(fileObj, runner())
			return

	operation().run_procedure(isAliveMin:int=None) # Calls the run procedure method with an is alive method checking every isAliveMin minutes
# or operation()()
    """
    def __init__(self, fileProviders:List[RepoObjectProvider], runners:List[Runner], loggersset:List[Logger]=[], enveloperset:List[Envelop]=[], perScan:Union[Callable, None] = None, general_prefix:Union[str, None]=None, log_debug_messages:bool=False, thread_count:int=1, use_results=False, seclusion_env:SeclusionEnv=None, seclusion_env_necessary_files=[]):
        """_summary_

        Args:
            fileProviders (List[RepoObjectProvider]): _description_
            runners (List[Runner]): _description_
            loggersset (List[Logger], optional): _description_. Defaults to [].
            enveloperset (List[Envelop], optional): _description_. Defaults to [].
            perScan (Union[Callable, None], optional): _description_. Defaults to None.
            general_prefix (Union[str, None], optional): _description_. Defaults to None.
            log_debug_messages (bool, optional): _description_. Defaults to False.
            thread_count (int, optional): _description_. Defaults to 1.
            use_results (bool, optional): _description_. Defaults to False.
            seclusion_env (SeclusionEnv, optional): _description_. Defaults to core_seclusion.
            seclusion_env_necessary_files (list, optional): _description_. Defaults to [].
        """

        self.uuid = mystring.string.of(str(uuid.uuid4()))
        self.fileProviders = fileProviders
        self.runners = runners

        self.perScan = perScan
        self.stage = None
        #https://superfastpython.com/asyncio-async-with/
        self.loggerSetLock = threading.Lock()
        self.loggerSet = LoggerSet(log_debug_messages = log_debug_messages,logger_queue_lock=self.loggerSetLock)
        for logger in loggersset:
            self.loggerSet.add(logger)

        self.envelopSet = EnvelopSet()
        for envelop in enveloperset:
            self.envelopSet.add(envelop)

        self.assets = []
        self.seclusion_env = seclusion_env

        for big_list in (fileProviders + runners + loggersset + enveloperset + [self.seclusion_env]):
            if isinstance(big_list, list):
                for core in big_list:
                    core.installImports()
                    self.assets += [core]
            else:
                big_list.installImports()
                self.assets += [big_list]

        if general_prefix:
            self.loggerSet.set_prefix(general_prefix)

        self.thread_count = thread_count
        self.thread_mgr = self.ThreadManager(max_threads=self.thread_count)

        self.use_results = use_results

        assets_packages = ["pnostic"]
        for asset in self.assets:
            assets_packages += [asset.imports]
        self.seclusion_env.python_packages(assets_packages)
        self.seclusion_env.setup_files(seclusion_env_necessary_files)

    def log(self, msg:Union[mystring.string, RepoObject, RepoResultObject]):
        """_summary_

        Args:
            msg (Union[mystring.string, RepoObject, RepoResultObject]): _description_
        """
        self.loggerSet.send(msg)

    class ThreadManager:
        """_summary_
        """
        def __init__(self, max_threads, use_results=False):
            self.max_threads = max_threads
            self.current_threads = []
            self.backup_threads = []
            self.lock = threading.Lock()

            self.thread_queue_completed_lock = threading.Lock()
            self.thread_queue_completed = True

            self.started_watching = False

            self.completed_threads_lock = threading.Lock()
            self.completed_threads = {}
            self.use_results = use_results

        @property
        def is_completed(self):
            with self.thread_queue_completed_lock:
                return self.thread_queue_completed

        def wait_until_completed(self):
            while not self.is_completed:
                yield False
            return True

        def result_of_thread(self, thread_id, check_every_x_sec=10):
            while True:
                with self.completed_threads_lock:
                    if thread_id in self.completed_threads:
                        return self.completed_threads[thread_id]
                time.sleep(check_every_x_sec)

        def add_thread(self, target_function, args=()):
            thread = ThreadWithReturnValue(target=target_function, args=args)

            with self.lock:
                if len(self.current_threads) < self.max_threads:
                    self.current_threads.append(thread)
                    thread.start()
                    self.thread_completed = False
                else:
                    self.backup_threads.append(thread)
                
                if not self.started_watching:
                    self.started_watching = True
                    asyncio.create_task(self.monitor_threads())
            
            return thread.native_id

        def check_completed_threads(self):
            with self.lock:
                completed_threads = [thread for thread in self.current_threads if not thread.is_alive()]

                for thread in completed_threads:
                    self.current_threads.remove(thread)
                    with self.completed_threads_lock:
                        self.completed_threads[thread.native_id] = True if not self.use_results else thread._return

                    if self.backup_threads:
                        new_thread = self.backup_threads.pop(0)
                        self.current_threads.append(new_thread)
                        new_thread.start()

            with self.thread_queue_completed_lock:
                self.thread_queue_completed = len(self.current_threads) == 0

        async def monitor_threads(self):
            while not self.is_completed:
                await asyncio.sleep(1)  # Adjust the sleep interval as needed
                self.check_completed_threads()

    @property
    def RepoObjects(self) -> List[RepoObject]:
        """_summary_

        Returns:
            List[RepoObject]: _description_

        Yields:
            Iterator[List[RepoObject]]: _description_
        """
        for fileProvider in self.fileProviders:
            for RepoObj in fileProvider.RepoObjects:
                RepoObj.uuid = mystring.string.of(str(uuid.uuid4()))
                self.envelopSet.per_next_repo_obj(RepoObj)
                yield RepoObj

    def __enter__(self):
        if self.stage:
            self.loggerSet.start(stage=self.stage)
        return self

    def __exit__(self, _type=None, value=None, traceback=None):
        if self.stage:
            self.loggerSet.end()
        return self

    @property
    def getRunnerProcedure(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        class RunnerProcedure(object):
            def __init__(self, runner:Runner, loggerSet, scanr):
                self.runner = runner
                self.loggerSet = loggerSet
                self.scanFile = scanr

            def log(self, msg:Union[mystring.string, RepoObject, RepoResultObject]):
                self.loggerSet.send("09: START LOG")
                self.loggerSet.send(msg)
                self.loggerSet.send("10: END LOG")

            def __call__(self) -> Runner:
                return self.runner

            def scan(self, fileObj):
                self.scanFile(fileObj, self.runner)

            def __enter__(self):
                self.loggerSet.send("11: START")
                self.runner.initialize()
                self.loggerSet.send("12: END START")
                return self

            def __exit__(self, _type=None, value=None, traceback=None):
                self.loggerSet.send("13: START")
                self.runner.clean()

        return lambda runner:RunnerProcedure(runner=runner, loggerSet=self.loggerSet, scanr=self.scan)

    def process(self, isAliveMin:int=None):
        """_summary_

        Args:
            isAliveMin (int, optional): _description_. Defaults to None.
        """
        with LoggerSet(self.loggerSet.loggers, stage="Stage 1: Starting the overall process := {0}".format(self.uuid)) as logy:
            def alive(min:int=None, loggerSet=None):
                import time
                while True:
                    loggerSet.send("14: Still Alive")
                    time.sleep(60 * min)

            aliveThread = None
            if isAliveMin:
                aliveThread = threading.Thread(target=alive, args=(isAliveMin, self.loggerSet), daemon = True)
                aliveThread.start()

            try:
                logy.send("15: Starting the procedure")
                self.run_procedure()
                while not self.thread_mgr.wait_until_completed():
                    time.sleep(10)

            except Exception as e:
                _, _, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logy.emergency(":> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))
            finally:
                logy.send("16: Closing the process")
        logy.send("17: Exiting the Scan := {0}".format(self.uuid))
        sys.exit(0)

    def __call__(self):
        return self.run_procedure()

    @abstractmethod
    def run_procedure(self):
        pass

    def scan(self, obj:RepoObject, runner:Runner, stage:mystring.string=None, notHollow:bool=False, wait_for_results=False)->List[RepoResultObject]:
        """_summary_

        Args:
            obj (RepoObject): _description_
            runner (Runner): _description_
            stage (mystring.string, optional): _description_. Defaults to None.
            notHollow (bool, optional): _description_. Defaults to False.
            wait_for_results (bool, optional): _description_. Defaults to False.

        Returns:
            List[RepoResultObject]: _description_
        """
        thread_id = self.thread_mgr.add_thread(self.scan_thread, args=(obj, runner, stage, notHollow))
        if wait_for_results:
            return self.thread_mgr.result_of_thread(thread_id=thread_id)
        else:
            return []

    def scan_thread(self, repoObj:RepoObject, runner:Runner, stage:mystring.string=None, notHollow:bool=False)-> List[RepoResultObject]:
        """_summary_

        Args:
            repoObj (RepoObject): _description_
            runner (Runner): _description_
            stage (mystring.string, optional): _description_. Defaults to None.
            notHollow (bool, optional): _description_. Defaults to False.

        Returns:
            List[RepoResultObject]: _description_
        """
        self.envelopSet.per_repo_obj_scan(repoObj, runner)
        output:List[RepoResultObject] = []
        if repoObj.is_dir and repoObj.file_scan_lambda is not None:
            for root, _, files in os.walk(repoObj.path):
                for file in files:
                    full_file_path = os.path.join(root, file)
                    if repoObj.file_scan_lambda(full_file_path):
                        full_file_obj = mystring.foil(full_file_path, preload=True)
                        output += self.scanObj(obj = RepoObject(
                            path=full_file_path,
                            hash=full_file_obj.hash_content(),
                            content=full_file_obj.content,
                            hasVuln=None,
                            cryVulnId=-1,
                            langPattern=None,
                            file_scan_lambda=None
                        ), runner = runner, stage = stage, notHollow = notHollow)
        else:
            output = self.scanObj(obj = repoObj, runner = runner, stage = stage, notHollow = notHollow)
        
        for repoObj in output:
            self.envelopSet.per_repo_obj_scan_result(repoObj, runner)
        
        return output

    def scanObj(self, obj:RepoObject, runner:Runner, stage:mystring.string=None, notHollow:bool=False)-> List[RepoResultObject]:
        """_summary_

        Args:
            obj (RepoObject): _description_
            runner (Runner): _description_
            stage (mystring.string, optional): _description_. Defaults to None.
            notHollow (bool, optional): _description_. Defaults to False.

        Returns:
            List[RepoResultObject]: _description_
        """
        from ephfile import ephfile

        exceptionString = None
        output:List[RepoResultObject] = []

        try:
            with LoggerSet(self.loggerSet.loggers, stage="Stage 2 Scanning {0} with {1} in procedure := [{2}] as run := [{3}]".format(obj.path, runner.name(), self.uuid, obj.uuid)) as logy:
                logy.send("18: Starting For Loop")
                try:
                    logy.send(obj)
                except Exception as e:
                    _,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    msg = "19: Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno)
                    self.loggerSet.emergency(msg)
                    logy.send(msg)


                execution_output = self.seclusion_env.process(obj, runner)
                startTime=execution_output.start_date_time
                endTime=execution_output.end_date_time
                output =execution_output.result

                logy.send("20: Finished Scanning {0} {1}".format(obj.str_type(), obj.path))
                if endTime is None:
                    endTime = startTime

                if not isinstance(output, list) and isinstance(output, list):
                    output = [output]

                if len(output) == 0 and notHollow:
                    output = [RepoResultObject.newEmpty(
                        projecttype=obj.path,
                        projectname=obj.path,
                        projecturl=None,
                        qual_name=None,
                        tool_name=runner.name(),
                        stage=stage,
                        ExceptionMsg=exceptionString,
                        startDateTime=None,
                        endDateTime=None
                    )]

                resultObject: RepoResultObject
                for resultObject in output:
                    try:
                        resultObject.startDateTime = set_time_wrapper(resultObject.startDateTime)
                        resultObject.endDateTime = set_time_wrapper(resultObject.endDateTime)

                        resultObject.uuid = obj.uuid
                        if stage:
                            resultObject.stage=stage
                        logy.send(resultObject)
                        if resultObject.Exception:
                            self.loggerSet.emergency(resultObject.Exception)
                    except Exception as e:
                        _,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        msg = ";> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno)
                        self.loggerSet.emergency(msg)
                        logy.send(msg)

        except Exception as e:
            import os,sys
            exceptionString = str(e)
            _,_, exc_tb = sys.exc_info();fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logy.emergency("|> Hit an unexpected error {0} @ {1}:{2}".format(e, fname, exc_tb.tb_lineno))

        if self.perScan:
            self.perScan()
        return output
