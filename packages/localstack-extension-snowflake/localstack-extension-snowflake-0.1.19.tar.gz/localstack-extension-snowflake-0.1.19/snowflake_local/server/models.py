_A=None
import dataclasses
@dataclasses.dataclass
class ApiResponse:
	success:bool=True;message:str|_A=_A;code:str|_A=_A
	def to_dict(A):return dataclasses.asdict(A)
class SnowflakeException(Exception):
	message:0
	def __init__(A,message):A.message=message
class QueryException(SnowflakeException):
	query_data:0;message:0
	def __init__(A,message,query_data):super().__init__(message=message);A.query_data=query_data
@dataclasses.dataclass
class QueryResponseData:queryId:str=_A;rowtype:list=dataclasses.field(default_factory=list);rowset:list=dataclasses.field(default_factory=list);rowsetBase64:str=_A;chunks:list=dataclasses.field(default_factory=list);chunkHeaders:dict=dataclasses.field(default_factory=dict);total:int=0;parameters:list[dict]=dataclasses.field(default_factory=list);queryResultFormat:str=_A;command:str=_A;src_locations:list[str]=_A;stageInfo:dict=_A;sourceCompression:str=_A;internalError:bool=_A;errorCode:str=_A;sqlState:str=_A;age:int=_A;line:int=_A;pos:int=_A;type:str=_A;statementTypeId:int=0
@dataclasses.dataclass
class QueryResponse(ApiResponse):data:QueryResponseData=dataclasses.field(default_factory=QueryResponseData)