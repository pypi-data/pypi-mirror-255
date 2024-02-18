import json,logging,os
from abc import ABC
from localstack.utils.objects import get_all_subclasses,singleton_factory
from sqlglot import exp
from snowflake_local import config
from snowflake_local.engine.models import Query
from snowflake_local.server.models import QueryResponse
from snowflake_local.utils.objects import get_full_class_name,load_class
LOG=logging.getLogger(__name__)
class QueryProcessor(ABC):
	def initialize_db_resources(A,database):0
	def should_apply(A,query):return True
	def transform_query(A,expression,query):return expression
	def postprocess_result(A,query,result):0
	def get_priority(A):return 0
	@classmethod
	def get_instances(A):return _get_instances()
@singleton_factory
def _get_instances():
	from snowflake_local.engine.processors import processor_class_names as B
	if B:C=[load_class(A)for A in B]
	else:C=get_all_subclasses(QueryProcessor)
	A=[A()for A in C];A=sorted([A for A in A],key=lambda item:item.get_priority(),reverse=True)
	if config.TRACE_LOG or os.environ.get('CI'):D=[get_full_class_name(A)for A in A];LOG.info('List of query processors: %s',json.dumps(D,indent=4))
	return A