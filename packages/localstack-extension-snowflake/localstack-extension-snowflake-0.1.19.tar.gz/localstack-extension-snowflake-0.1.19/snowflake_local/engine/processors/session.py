_D='TEST'
_C='is_string'
_B='this'
_A=True
import json,re
from sqlglot import exp
from snowflake_local.engine.models import Query
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import NameType,get_canonical_name
from snowflake_local.server.models import QueryResponse
ACCOUNT_ID='TESTACC123'
class InsertSessionId(QueryProcessor):
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Func)and str(A.this).lower()=='current_session':return exp.Literal(this=query.session.session_id,is_string=_A)
		return A
class UpdateSessionAfterCreatingSchema(QueryProcessor):
	REGEX=re.compile('^\\s*CREATE.*\\s+SCHEMA(\\s+IF\\s+NOT\\s+EXISTS)?\\s+(\\S+)',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def postprocess_result(B,query,result):A=query;C=B.REGEX.match(A.original_query);A.session.schema=C.group(2)
class UpdateSessionAfterCreatingDatabase(QueryProcessor):
	REGEX=re.compile('^\\s*CREATE.*\\s+DATABASE(\\s+IF\\s+NOT\\s+EXISTS)?\\s+(\\S+)',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def postprocess_result(B,query,result):A=query;C=B.REGEX.match(A.original_query);A.session.database=get_canonical_name(C.group(2),quoted=False,type=NameType.DATABASE);A.session.schema=None
class ReplaceCurrentAccount(QueryProcessor):
	def transform_query(D,expression,**E):
		B=expression;C=['CURRENT_ACCOUNT','CURRENT_ACCOUNT_NAME']
		if isinstance(B,exp.Func)and str(B.this).upper()in C:A=exp.Literal();A.args[_B]=ACCOUNT_ID;A.args[_C]=_A;return A
		if isinstance(B,exp.CurrentUser):A=exp.Literal();A.args[_B]=_D;A.args[_C]=_A;return A
		return B
class ReplaceCurrentWarehouse(QueryProcessor):
	def transform_query(D,expression,query):
		C=query;A=expression
		if isinstance(A,exp.Func)and str(A.this).upper()=='CURRENT_WAREHOUSE':B=exp.Literal();B.args[_B]=C.session and C.session.warehouse or _D;B.args[_C]=_A;return B
		return A
class ReplaceCurrentStatement(QueryProcessor):
	def transform_query(C,expression,query):
		A=expression
		if isinstance(A,exp.Func)and str(A.this).upper()=='CURRENT_STATEMENT':B=exp.Literal();B.args[_B]=query.original_query;B.args[_C]=_A;return B
		return A
class DefineCurrentSessionInfoFunctions(QueryProcessor):
	def initialize_db_resources(H,database):
		D='PUBLIC';E=['ACCOUNTADMIN','ORGADMIN',D,'SECURITYADMIN','SYSADMIN','USERADMIN'];F={'current_account':'TEST001','current_account_name':'TEST002','current_available_roles':json.dumps(E),'current_client':'test-client','current_ip_address':'127.0.0.1','current_organization_name':'TESTORG','current_region':'TEST_LOCAL','get_current_role':D,'get_current_user':_D,'current_role_type':'ROLE','current_secondary_roles':json.dumps({'roles':'','value':''}),'current_version':'0.0.0','current_transaction':None};C=[]
		for(G,B)in F.items():B=B and f"'{B}'";A=f"\n                CREATE OR REPLACE FUNCTION {get_canonical_name(G)} ()\n                RETURNS TEXT LANGUAGE plpython3u IMMUTABLE AS $$ return {B} $$\n            ";C.append(A)
		A='\n        CREATE OR REPLACE FUNCTION information_schema.CURRENT_TASK_GRAPHS() RETURNS\n        TABLE(\n            ROOT_TASK_NAME TEXT, DATABASE_NAME TEXT, SCHEMA_NAME TEXT, STATE TEXT, SCHEDULED_FROM TEXT,\n            FIRST_ERROR_TASK_NAME TEXT, FIRST_ERROR_CODE NUMERIC, FIRST_ERROR_MESSAGE TEXT,\n            SCHEDULED_TIME TIMESTAMP, QUERY_START_TIME TIMESTAMP, NEXT_SCHEDULED_TIME TIMESTAMP,\n            ROOT_TASK_ID TEXT, GRAPH_VERSION NUMERIC, RUN_ID NUMERIC, ATTEMPT_NUMBER NUMERIC,\n            CONFIG TEXT, GRAPH_RUN_GROUP_ID NUMERIC\n        )\n        LANGUAGE plpython3u IMMUTABLE AS $$ return [] $$;\n        ';A=f"{A}; {'; '.join(C)}";State.server.run_query(A,database=database)