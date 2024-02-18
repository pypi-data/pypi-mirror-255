import base64,logging,re,uuid
from typing import Any
from localstack.utils.strings import to_bytes,to_str,truncate
from pg8000.dbapi import ProgrammingError
from sqlglot import parse_one
from snowflake_local import config
from snowflake_local.engine.db_engine import get_db_engine
from snowflake_local.engine.models import Query,QueryResult,QueryState,Session
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.session import APP_STATE,handle_use_query
from snowflake_local.engine.transform_utils import get_canonical_name
from snowflake_local.engine.transforms import remove_comments
from snowflake_local.files.file_ops import handle_copy_into_query,handle_put_file_query
from snowflake_local.server.models import QueryException,QueryResponse,QueryResponseData
LOG=logging.getLogger(__name__)
def cleanup_query(query):
	D='/\\*.*?\\*/';C='snowflake';B=query;A=B.strip(' ;')
	try:
		if re.match('.*DESC(RIBE)?.+FILE\\s+FORMAT',B,flags=re.I|re.M):raise Exception
		E=parse_one(A,read=C);F=E.transform(remove_comments);A=str(F.sql(dialect=C));A=re.sub(D,'',A,flags=re.I)
	except Exception:A=re.sub(D,'',A,flags=re.I);A=re.sub('^\\s*--.*','',A,flags=re.M)
	return A
def execute_query(query):A=query;B=get_db_engine();A=prepare_query(A);C=B.execute_query(A);return C
def prepare_query(query_obj):A=query_obj;A.original_query=A.query;A.query=_create_tmp_table_for_file_queries(A.query);B=get_db_engine();A=B.prepare_query(A);return A
def insert_rows_into_table(table,rows,schema=None,database=None):
	J=database;I=schema;H=', ';A=rows;E=f'"{table}"'
	if I:E=f"{get_canonical_name(I)}.{E}"
	if A and isinstance(A[0],dict):
		B=set()
		for C in A:B.update(C.keys())
		B=list(B);F=B
		if config.CONVERT_NAME_CASING:F=[f'"{A}"'for A in B]
		F=H.join(F);G=H.join(['?'for A in B]);K=f"INSERT INTO {E} ({F}) VALUES ({G})"
		for C in A:L=[C.get(A)for A in B];D=Query(query=K,params=list(L),database=J);execute_query(D)
	elif A and isinstance(A[0],(list,tuple)):
		for C in A:M=len(C);G=H.join(['?'for A in range(M)]);D=f"INSERT INTO {E} VALUES ({G})";D=Query(query=D,params=list(C),database=J);execute_query(D)
	elif A:raise Exception(f"Unexpected values when storing list of rows to table: {truncate(str(A))}")
def handle_query_request(query,params,session,request):
	O='type';N='002002';M=False;L='name';G=session;B=query;A=QueryResponse();A.data.parameters.append({L:'TIMEZONE','value':'UTC'});B=cleanup_query(B);H=A.data.queryId=str(uuid.uuid4());C=Query(query_id=H,query=B,params=params,session=G,request=request);APP_STATE.queries[H]=P=QueryState(query=C,query_state='RUNNING');Q=re.match('^\\s*PUT\\s+.+',B,flags=re.I)
	if Q:return handle_put_file_query(B,A)
	R=re.match('^\\s*COPY\\s+INTO\\s.+',B,flags=re.I)
	if R:return handle_copy_into_query(C,A)
	S=re.match('^\\s*USE\\s.+',B,flags=re.I)
	if S:return handle_use_query(B,A,G)
	if(T:=re.match('^\\s*CREATE.*\\s+WAREHOUSE(\\s+IF\\s+NOT\\s+EXISTS)?\\s+(\\S+)',B,flags=re.I)):G.warehouse=T.group(2);return A
	if re.match('^\\s*DROP.*\\s+WAREHOUSE',B,flags=re.I):G.warehouse=None;return A
	U=re.match('^\\s*CREATE\\s+STORAGE\\s.+',B,flags=re.I)
	if U:return A
	try:E=execute_query(C)
	except Exception as D:
		V=LOG.exception if config.TRACE_LOG else LOG.warning;V('Error executing query: %s',D);A.success=M;A.message=str(D)
		if isinstance(D,ProgrammingError)and D.args:A.code=N;A.message=D.args[0].get('M')or str(D);A.data=QueryResponseData(**{'internalError':M,'errorCode':N,'age':0,'sqlState':'42710','queryId':H,'line':-1,'pos':-1,O:'COMPILATION'})
		for F in QueryProcessor.get_instances():
			if F.should_apply(C):F.postprocess_result(C,result=A)
		raise QueryException(message=A.message,query_data=A)from D
	P.result=E
	if E and E.columns:
		I=[];W=E.columns
		for X in E.rows:I.append(list(X))
		K=[]
		for J in W:K.append({L:J.name,O:J.type_name,'length':J.type_size,'precision':0,'scale':0,'nullable':True})
		A.data.rowset=I;A.data.rowtype=K;A.data.total=len(I)
	for F in QueryProcessor.get_instances():
		if F.should_apply(C):F.postprocess_result(C,result=A)
	return A
def _create_tmp_table_for_file_queries(query):
	A=query;B='(.*SELECT\\s+.+\\sFROM\\s+)(@[^\\(\\s]+)(\\s*\\([^\\)]+\\))?';C=re.match(B,A)
	if not C:return A
	def D(match):A=match;B=to_str(base64.b64encode(to_bytes(A.group(3)or'')));return f"{A.group(1)} load_data('{A.group(2)}', '{B}') as _tmp"
	A=re.sub(B,D,A);return A