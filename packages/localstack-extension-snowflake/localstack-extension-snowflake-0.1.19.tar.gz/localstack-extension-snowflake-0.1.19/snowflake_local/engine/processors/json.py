import json
from localstack.utils.json import extract_jsonpath
from localstack.utils.numbers import is_number
from snowflake_local.engine.models import VARIANT
from snowflake_local.engine.postgres.constants import PG_VARIANT_TYPE
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import get_canonical_name,to_variant,unwrap_variant_type
class HandleGetPath(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
        CREATE OR REPLACE FUNCTION {get_canonical_name("get_path")} (obj {PG_VARIANT_TYPE}, path TEXT) RETURNS TEXT
        LANGUAGE plpython3u IMMUTABLE AS $$
            from snowflake_local.engine.processors.json import HandleGetPath
            return HandleGetPath.get_path(obj, path)
        $$
        """;A.run_query(B,database=database)
	@classmethod
	def get_path(D,obj,path):
		C=obj;B=path
		if not B.startswith('.'):B=f".{B}"
		if not B.startswith('$'):B=f"${B}"
		if C is not None and not isinstance(C,(list,dict)):C=unwrap_variant_type(C,expected_type=(list,dict))
		A=extract_jsonpath(C,B)
		if A==[]:return''
		if is_number(A)and not isinstance(A,bool)and int(A)==A:A=int(A)
		A=json.dumps(A);return A
class HandleParseJson(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("parse_json")} (obj TEXT) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.json import HandleParseJson
                return HandleParseJson.parse_json(obj)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def parse_json(B,obj):
		if str(obj).upper()=='NULL':return to_variant('null')
		A=json.loads(obj);return to_variant(A)
class HandleObjectConstruct(QueryProcessor):
	def initialize_db_resources(F,database):
		A=[]
		for B in range(10):C=', '.join([f"k{A} TEXT, v{A} TEXT"for A in range(B)]);D=', '.join([f"k{A}, v{A}"for A in range(B)]);A.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name("object_construct")} ({C}) RETURNS {PG_VARIANT_TYPE}
                LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.json import HandleObjectConstruct
                    return HandleObjectConstruct.object_construct({D})
                $$
            """)
		E='; '.join(A);State.server.run_query(E,database=database)
	@classmethod
	def object_construct(E,*A,**F):
		B={}
		for C in range(0,len(A),2):D=A[C+1];B[A[C]]=unwrap_variant_type(D)
		return to_variant(B)