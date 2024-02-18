from snowflake_local.engine.postgres.constants import PG_VARIANT_TYPE,PG_VARIANT_TYPES_AND_ARRAYS
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import get_canonical_name
class HandleCancelAllQueries(QueryProcessor):
	def initialize_db_resources(D,database):
		B=State.server;A=[]
		for E in PG_VARIANT_TYPES_AND_ARRAYS:A.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name("system$cancel_all_queries")} (session TEXT)
                RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.system import HandleCancelAllQueries
                    return HandleCancelAllQueries.cancel_all_queries(session)
                $$
            """)
		C='; '.join(A);B.run_query(C,database=database)
	@classmethod
	def cancel_all_queries(A,session):return'canceled'
class HandleStreamingOffsetToken(QueryProcessor):
	def initialize_db_resources(B,database):A=f'''
            CREATE OR REPLACE FUNCTION {get_canonical_name("system$snowpipe_streaming_migrate_channel_offset_token")} (
                tableName TEXT, channelName TEXT, offsetToken TEXT) RETURNS TEXT
            LANGUAGE plpython3u IMMUTABLE AS $$
                # TODO: simply returning hardcoded value for now - may need to get adjusted over time
                return \'{{"responseMessage":"Success","responseCode":50}}\'
            $$
        ''';State.server.run_query(A,database=database)