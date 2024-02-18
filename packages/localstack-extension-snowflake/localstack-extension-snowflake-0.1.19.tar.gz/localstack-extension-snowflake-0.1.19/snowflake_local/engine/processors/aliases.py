from localstack.utils.strings import short_uid
from sqlglot import exp
from snowflake_local.engine.processors.aggregates import ConvertArrayAggParams
from snowflake_local.engine.processors.identifiers import HandleDollarReferences
from snowflake_local.engine.query_processors import QueryProcessor
class UnwrapMultiNestedSubqueries(QueryProcessor):
	def transform_query(C,expression,**D):
		B=expression
		if isinstance(B,exp.Subquery):
			A=B
			while isinstance(A.this,exp.Subquery)and not A.this.alias:A=A.this
			return A
		return B
class AddAliasToSubquery(QueryProcessor):
	def transform_query(B,expression,**C):
		A=expression
		if isinstance(A,(exp.Subquery,exp.Values)):
			if A.alias or not A.parent_select:return A
			if isinstance(A.parent,exp.Union):return A
			A.args['alias']=exp.TableAlias(this=f"_tmp{short_uid()}")
		return A
	def get_priority(B):A=[UnwrapMultiNestedSubqueries().get_priority(),ConvertArrayAggParams().get_priority()];return min(A)-1
class AddColumnNamesToTableAliases(QueryProcessor):
	def transform_query(J,expression,**K):
		A=expression
		if not isinstance(A,exp.From):return A
		C=A.this;F=isinstance(C,exp.Table)and isinstance(C.this,exp.Anonymous)and str(C.this.this).lower()=='load_data'
		if not F and not isinstance(A.this,exp.Values):return A
		if not A.parent_select:return A
		G=[]
		for B in A.parent_select.expressions or[]:
			if isinstance(B,exp.Alias):B=B.this
			if isinstance(B,exp.Cast):B=B.this
			if isinstance(B,exp.Identifier):G.append(B.this)
		D=A.this.args.get('alias')
		if not isinstance(D,exp.TableAlias):return A
		H=D.args['columns']=D.columns or[]
		for I in G:
			E=exp.ColumnDef();E.args['this']=exp.Identifier(this=I,quoted=False)
			if F:E.args['kind']=exp.DataType.build('TEXT')
			H.append(E)
		return A
	def get_priority(B):A=[HandleDollarReferences().get_priority(),AddAliasToSubquery().get_priority()];return min(A)-1