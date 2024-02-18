import dataclasses,logging,re
from localstack.http import Request
from snowflake_local.engine.models import QueryState,Session
from snowflake_local.engine.transform_utils import NameType,get_canonical_name
from snowflake_local.server.models import QueryResponse
LOG=logging.getLogger(__name__)
@dataclasses.dataclass
class DBResources:file_formats:dict[str,dict]=dataclasses.field(default_factory=dict)
@dataclasses.dataclass
class ApplicationState:sessions:dict[str,Session]=dataclasses.field(default_factory=dict);queries:dict[str,QueryState]=dataclasses.field(default_factory=dict);db_resources:dict[str,DBResources]=dataclasses.field(default_factory=dict)
APP_STATE=ApplicationState()
def handle_use_query(query,result,session):
	G=False;F=result;E=query;A=session;B=re.match('^\\s*USE\\s+(\\S+)\\s+(\\S+)',E,flags=re.I)
	if not B:return F
	D=B.group(1).strip().lower();C=get_canonical_name(B.group(2),quoted=G)
	if D=='database':A.database=get_canonical_name(B.group(2),quoted=G,type=NameType.DATABASE);A.schema=None
	elif D=='warehouse':A.warehouse=C
	elif D=='schema':
		A.schema=C
		if'.'in C:A.database,A.schema=C.split('.')
	else:LOG.info("Unexpected 'USE ...' query: %s",E)
	return F
def get_auth_token_from_request(request):A=request.headers.get('Authorization')or'';A=A.removeprefix('Snowflake ').strip();A=A.split('Token=')[-1].strip('\'"');return A
def lookup_request_session(request):
	B=get_auth_token_from_request(request)
	for A in APP_STATE.sessions.values():
		if A.auth_token==B:return A