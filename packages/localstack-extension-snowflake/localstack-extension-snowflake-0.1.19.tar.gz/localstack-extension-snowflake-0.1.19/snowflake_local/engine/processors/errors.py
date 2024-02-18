_A='already exists'
import logging,re
from snowflake_local.engine.models import Query
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.server.models import QueryResponse
LOG=logging.getLogger(__name__)
class FixAlreadyExistsErrorResponse(QueryProcessor):
	def postprocess_result(C,query,result):
		A=result
		if A.success or _A not in(A.message or''):return
		def B(match):return f"SQL compilation error:\nObject '{match.group(1).upper()}' already exists."
		A.message=re.sub('.*database \\"(\\S+)\\".+',B,A.message);A.message=re.sub('.*relation \\"(\\S+)\\".+',B,A.message);A.message=re.sub('.*function \\"(\\S+)\\".+',B,A.message)
class IgnoreErrorForExistingEntity(QueryProcessor):
	REGEX=re.compile('^\\s*CREATE.*\\s+(\\S+)(\\s+IF\\s+NOT\\s+EXISTS)\\s+(\\S+)',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def postprocess_result(B,query,result):
		A=result
		if not A.success and _A in(A.message or''):A.success=True;A.data.rowtype=[];A.data.rowset=[]