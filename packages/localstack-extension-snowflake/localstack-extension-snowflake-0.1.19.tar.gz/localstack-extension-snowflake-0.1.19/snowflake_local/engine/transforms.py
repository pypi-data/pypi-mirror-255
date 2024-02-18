import logging,re
from aenum import extend_enum
from sqlglot import TokenType,exp,parse_one,tokens
from sqlglot.dialects import Postgres,Snowflake
from snowflake_local.engine.models import Query
LOG=logging.getLogger(__name__)
def apply_query_transforms(query):
	A=query;import snowflake_local.engine.processors;from snowflake_local.engine.query_processors import QueryProcessor as E
	if isinstance(A,str):A=Query(query=A)
	A.query=apply_query_fixes(A.query);B=parse_one(A.query,read='snowflake')
	for C in E.get_instances():
		if C.should_apply(A):
			D=B.transform(C.transform_query,query=A)
			if isinstance(D,exp.Expression):B=D
			else:LOG.warning('Query transformer %s returned unexpected result: %s',C,D)
	A.query=B.sql(dialect='postgres');return A
def apply_query_fixes(query):A=query;A=re.sub('(\\s*ALTER\\s+TABLE\\s+.*CLUSTER\\s+BY\\s+)([^\\s()]+)','\\1(\\2)',A,flags=re.I);return A
def remove_comments(expression,**B):
	A=expression
	if isinstance(A,exp.Comment):return exp.Literal(this='',is_string=False)
	if A.comments:A.comments=None
	return A
def _patch_sqlglot():
	Snowflake.Parser.FUNCTIONS.pop('OBJECT_CONSTRUCT',None);Snowflake.Parser.FUNCTIONS.pop('ARRAY_GENERATE_RANGE',None)
	if len(exp.ArraySort.arg_types)<3:exp.ArraySort.arg_types['nulls_first']=False
	for A in('ANYARRAY','ANYELEMENT'):
		extend_enum(TokenType,A,A);extend_enum(exp.DataType.Type,A,A);D=getattr(exp.DataType.Type,A);B=getattr(exp.DataType.Type,A);tokens.Tokenizer.KEYWORDS[A]=B
		for C in(Postgres,Snowflake):C.Parser.TYPE_TOKENS.add(B);C.Parser.ID_VAR_TOKENS.add(B);C.Parser.FUNC_TOKENS.add(B);C.Generator.TYPE_MAPPING[D]=A;C.Tokenizer.KEYWORDS[A]=B
_patch_sqlglot()