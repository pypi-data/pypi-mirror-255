from abc import ABC,abstractmethod
from snowflake_local import config
from snowflake_local.engine.models import Query,QueryResult
class DBEngine(ABC):
	@abstractmethod
	def execute_query(self,query):0
	@abstractmethod
	def prepare_query(self,query):0
def get_db_engine():
	if config.DB_ENGINE=='postgres':from snowflake_local.engine.postgres.db_engine_postgres import DBEnginePostgres as A;return A()
	raise Exception(f"Unknown DB engine '{config.DB_ENGINE}'")