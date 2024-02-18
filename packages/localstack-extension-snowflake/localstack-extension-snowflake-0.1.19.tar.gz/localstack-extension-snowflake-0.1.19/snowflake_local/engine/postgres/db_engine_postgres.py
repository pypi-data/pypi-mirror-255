_D='TIMESTAMP WITH TIME ZONE'
_C='TIMESTAMP WITHOUT TIME ZONE'
_B='VARCHAR'
_A='test'
import atexit,logging,time
from localstack import config
from localstack.utils.net import get_free_tcp_port,wait_for_port_open
from localstack_ext.packages.postgres import postgresql_package
from localstack_ext.services.rds.engine_postgres import get_type_name
from localstack_ext.utils.postgresql import Postgresql
from snowflake_local import config as sf_config
from snowflake_local.engine.db_engine import DBEngine
from snowflake_local.engine.models import Query,QueryResult,TableColumn
from snowflake_local.engine.packages import POSTGRES_VERSION,postgres_plv8_package
from snowflake_local.engine.postgres.constants import DEFAULT_DATABASE
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.transform_utils import NameType,get_canonical_name,get_database_from_drop_query
from snowflake_local.engine.transforms import apply_query_transforms
LOG=logging.getLogger(__name__)
class DBEnginePostgres(DBEngine):
	def execute_query(G,query):
		A=_execute_query(query)
		if isinstance(A,list):return QueryResult(rows=A)
		B=QueryResult();B.row_count=A._context.row_count
		if not A._context.columns:return B
		C=list(A);C=[tuple(A)for A in C];B.rows=C
		for D in A._context.columns:E=D['name'].upper();F=TableColumn(name=E,type_name=get_pg_type_name(D['type_oid']),type_size=D['type_size']);B.columns.append(F)
		return B
	def prepare_query(A,query):return apply_query_transforms(query)
def _execute_query(query):
	A=query;G=_start_postgres();E=bool(get_database_from_drop_query(A.original_query));D=A.query;B=None
	if A.session:
		if A.session.database:B=A.session.database
		if A.session.schema and A.session.schema!='public'and not E:
			C=A.session.schema
			if'.'in C:B,C=C.split('.')
			C=get_canonical_name(C);D=f"SET search_path TO {C}, public; \n{D}"
	B=A.database or B or DEFAULT_DATABASE
	if E:B=None
	else:
		B=get_canonical_name(B,quoted=False,type=NameType.DATABASE)
		try:_define_util_functions(B)
		except Exception as H:LOG.warning('Unable to define Postgres util functions: %s',H);raise
	F=A.params or[];LOG.debug('Running query (DB %s): %s - %s',B,D,F);return G.run_query(D,*F,database=B)
def _start_postgres(user=_A,password=_A,database=_A):
	if not State.server:
		if config.is_in_docker:postgresql_package.install(version=POSTGRES_VERSION)
		A=get_free_tcp_port();State.server=Postgresql(port=A,user=user,password=password,database=database,boot_timeout=30,include_python_venv_libs=True,pg_version=POSTGRES_VERSION);time.sleep(1)
		try:wait_for_port_open(A,retries=20,sleep_time=.8)
		except Exception as B:raise Exception('Unable to start up Postgres process (health check failed after 10 secs)')from B
		def C():State.server.terminate()
		atexit.register(C)
	return State.server
def _define_util_functions(database):
	A=database;from snowflake_local.engine.query_processors import QueryProcessor as C
	if A in State.initialized_dbs:return
	State.initialized_dbs.append(A);B=State.server
	if sf_config.CONVERT_NAME_CASING and A.upper()==DEFAULT_DATABASE.upper():B.run_query(f'CREATE DATABASE "{DEFAULT_DATABASE.upper()}"')
	B.run_query('CREATE EXTENSION IF NOT EXISTS plpython3u',database=A);D=[];E=';\n'.join(D);B.run_query(E,database=A)
	for F in C.get_instances():F.initialize_db_resources(database=A)
def install_plv8_extension():
	if config.is_in_docker:postgres_plv8_package.install()
def get_pg_type_name(scalar_type):
	A=scalar_type;C={'19':_B,'25':_B,'1114':_C,'1184':_D};B=C.get(str(A))
	if B:return B
	return get_type_name(A)
def convert_pg_to_snowflake_type(pg_type):
	A=pg_type;A=str(A).upper()
	if A==_C:return'TIMESTAMP_NTZ'
	if A==_D:return'TIMESTAMP_TZ'
	if A in('CHARACTER VARYING',_B):return'TEXT'
	return A