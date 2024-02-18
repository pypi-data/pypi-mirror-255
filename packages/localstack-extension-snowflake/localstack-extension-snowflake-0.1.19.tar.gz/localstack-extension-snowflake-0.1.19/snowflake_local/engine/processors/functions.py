from localstack.utils.strings import to_bytes
from sqlglot import exp
from snowflake_local.engine.models import Query
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
class FixFunctionCodeEscaping(QueryProcessor):
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.Create)and str(A.args.get('kind')).upper()=='FUNCTION'and isinstance(A.expression,exp.Literal):B=to_bytes(A.expression.this).decode('unicode_escape');A.expression.args['this']=B
		return A
class LoadJavaScriptFunctionExtension(QueryProcessor):
	def transform_query(F,expression,query,**G):
		A=expression
		if not isinstance(A,exp.Create):return A
		if not isinstance(A.this,exp.UserDefinedFunction):return A
		C=A.args['properties'].expressions;B=[A for A in C if isinstance(A,exp.LanguageProperty)];B=str(B[0].this).lower()if B else None
		if B in('javascript','plv8'):
			D=query.get_database()
			try:from snowflake_local.engine.postgres.db_engine_postgres import install_plv8_extension as E;E();State.server.run_query('CREATE EXTENSION IF NOT EXISTS plv8',database=D)
			except ModuleNotFoundError:pass
		return A
class PrefixRawExpressionWithSelect(QueryProcessor):
	def transform_query(D,expression,**E):
		A=expression;C=exp.Identifier,exp.Cast,exp.Literal
		if not A.parent and isinstance(A,C):B=exp.Select();B.args['expressions']=[A];return B
		return A