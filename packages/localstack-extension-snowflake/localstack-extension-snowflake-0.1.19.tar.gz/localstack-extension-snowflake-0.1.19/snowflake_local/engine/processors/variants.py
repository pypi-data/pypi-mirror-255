from localstack.utils.collections import ensure_list
from sqlglot import exp
from snowflake_local.engine.query_processors import QueryProcessor
class ReplaceObjectConstruct(QueryProcessor):
	def transform_query(E,expression,**F):
		A=expression
		if isinstance(A,exp.Func)and str(A.this).upper()=='OBJECT_CONSTRUCT':
			B=A.args['expressions']
			for C in range(1,len(B),2):D=B[C];B[C]=exp.Anonymous(this='to_variant',expressions=ensure_list(D))
		return A