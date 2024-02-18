from sqlglot import exp
from snowflake_local.engine.models import Query
from snowflake_local.engine.query_processors import QueryProcessor
class HandleRatioToReport(QueryProcessor):
	ROUND_DECIMALS=6
	def transform_query(C,expression,query):
		A=expression
		if not isinstance(A,exp.Window):return A
		B=A.this
		if isinstance(B,exp.Anonymous)and str(B.this).lower()=='ratio_to_report':B.args['this']='sum';D=exp.Cast(this=B.expressions[0],to=exp.DataType.build('DECIMAL'));E=exp.Div(this=D,expression=A,typed=True);round=exp.Round(this=E,decimals=exp.Literal(this=str(C.ROUND_DECIMALS),is_string=False));F=exp.Cast(this=round,to=exp.DataType.build('TEXT'));return F
		return A