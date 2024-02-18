_A=None
from typing import Any
from localstack.utils.strings import to_bytes
from snowflake_local.engine.models import VARIANT
from snowflake_local.engine.postgres.constants import PG_VARIANT_COMPATIBLE_TYPES,PG_VARIANT_TYPE,PG_VARIANT_TYPES_AND_ARRAYS
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import get_canonical_name,to_variant
class HandleToVariant(QueryProcessor):
	def initialize_db_resources(E,database):
		B=State.server;A=[]
		for C in PG_VARIANT_TYPES_AND_ARRAYS:A.append(f"""
                    CREATE OR REPLACE FUNCTION {get_canonical_name("to_variant")} (obj {C}) RETURNS {PG_VARIANT_TYPE}
                    LANGUAGE plpython3u IMMUTABLE AS $$
                        from snowflake_local.engine.processors.conversions import HandleToVariant
                        return HandleToVariant.to_variant(obj)
                    $$
                """)
		D='; '.join(A);B.run_query(D,database=database)
	@classmethod
	def to_variant(A,obj):return to_variant(obj,external=True)
	def get_priority(A):return 20
class HandleToBoolean(QueryProcessor):
	def initialize_db_resources(E,database):
		B=State.server;A=[]
		for C in PG_VARIANT_COMPATIBLE_TYPES:A.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name("to_boolean")} (obj {C}) RETURNS BOOLEAN
                LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.conversions import HandleToBoolean
                    return HandleToBoolean.to_boolean(obj)
                $$
            """)
		D='; '.join(A);B.run_query(D,database=database)
	@classmethod
	def to_boolean(C,obj):
		B=False;A=obj
		if A is _A:return B
		if A=='true':return True
		if A=='false':return B
		return bool(A)
class HandleToBinary(QueryProcessor):
	DEFAULT_ENCODING='UTF-8'
	def initialize_db_resources(C,database):A='to_binary';B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)} (_obj TEXT) RETURNS BYTEA
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.conversions import HandleToBinary
                return HandleToBinary.to_binary(_obj)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)} (_obj TEXT, _format TEXT) RETURNS BYTEA
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.conversions import HandleToBinary
                return HandleToBinary.to_binary(_obj, _format)
            $$
        """;State.server.run_query(B,database=database)
	@classmethod
	def to_binary(B,_obj,_format=_A):A=_format;A=A or B.DEFAULT_ENCODING;return str(_obj).encode(A)
class HandleToChar(QueryProcessor):
	def initialize_db_resources(D,database):
		A=[]
		for B in PG_VARIANT_COMPATIBLE_TYPES+('BYTEA',):A.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name("to_char")} (obj {B}) RETURNS TEXT
                LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.conversions import HandleToChar
                    return HandleToChar.to_char(obj)
                $$
            """)
		C='; '.join(A);State.server.run_query(C,database=database)
	@classmethod
	def to_char(D,obj,format=_A):
		B=obj
		if isinstance(B,bytes):C=''.join(f"{A:0x}"for A in B);return C.upper()
		if B is _A:return B
		A=str(B)
		if len(A)>=2 and A[0]==A[-1]=='"':return A[1:-1]
		A=to_bytes(A).decode('unicode_escape');return A