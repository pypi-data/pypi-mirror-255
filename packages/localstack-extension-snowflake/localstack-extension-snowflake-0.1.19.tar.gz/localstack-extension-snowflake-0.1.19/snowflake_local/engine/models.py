_A=None
import dataclasses,datetime
from enum import Enum
from sqlglot import exp
from snowflake_local.engine.postgres.constants import DEFAULT_DATABASE
AGG_COMPARABLE_TYPE=float|datetime.datetime
VARIANT=str
VARIANT_MARKER_PREFIX='=VARIANT::'
VARIANT_EXT_MARKER_PREFIX='=VARIANT::EXT::'
@dataclasses.dataclass
class SystemState:
	_instance=_A;parameters:dict[str,str]=dataclasses.field(default_factory=dict)
	@classmethod
	def get(A):A._instance=A._instance or SystemState();return A._instance
@dataclasses.dataclass
class Session:session_id:str;auth_token:str|_A=_A;warehouse:str|_A=_A;schema:str|_A=_A;database:str|_A=_A;parameters:dict[str,str]=dataclasses.field(default_factory=dict);system_state:SystemState=dataclasses.field(default_factory=SystemState.get)
@dataclasses.dataclass
class Query:
	query:str|exp.Expression;query_id:str|_A=_A;original_query:str|exp.Expression|_A=_A;params:list|_A=_A;database:str|_A=_A;session:Session|_A=_A;request:dict|_A=_A
	def __post_init__(A,*B,**C):
		if A.query and not A.original_query:A.original_query=A.query
	def get_database(A):from snowflake_local.engine.transform_utils import get_canonical_name as B;return A.database or(A.session.database if A.session else _A)or B(DEFAULT_DATABASE,quoted=False)
@dataclasses.dataclass
class TableColumn:name:str;type_name:str;type_size:int=0
@dataclasses.dataclass
class QueryResult:rows:list[tuple]=dataclasses.field(default_factory=list);columns:list[TableColumn]=dataclasses.field(default_factory=list);row_count:int=0
@dataclasses.dataclass
class QueryState:query:Query;query_state:str|_A=_A;result:QueryResult|_A=_A
class StatementType(Enum):UNKNOWN=0;SELECT=4096;DML=12288;INSERT=12288+256;UPDATE=12288+512;DELETE=12288+768;MERGE=12288+1024;MULTI_INSERT=12288+1280;COPY=12288+1536;UNLOAD=12288+1792;RECLUSTER=12288+2048;SCL=16384;ALTER_SESSION=16384+256;USE=16384+768;USE_DATABASE=16384+768+1;USE_SCHEMA=16384+768+2;USE_WAREHOUSE=16384+768+3;SHOW=16384+1024;DESCRIBE=16384+1280;LIST=16384+1792+1;TCL=20480;DDL=24576;GET=28672+256+1;PUT=28672+256+2;REMOVE=28672+256+3