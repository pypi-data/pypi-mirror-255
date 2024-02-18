_G='javascript'
_F='properties'
_E='TABLE'
_D=None
_C='quoted'
_B=False
_A='this'
import textwrap
from localstack.utils.numbers import is_number
from sqlglot import exp
from snowflake_local import config
from snowflake_local.engine.models import Query
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import INTERNAL_IDENTIFIERS,NameType,get_canonical_name,is_create_table_expression
from snowflake_local.engine.transforms import apply_query_transforms
class TrackCaseSensitiveIdentifiers(QueryProcessor):
	def transform_query(J,expression,query):
		E='SCHEMA';D='DATABASE';B=expression;from snowflake_local.engine.postgres.db_state import State
		if isinstance(B,exp.Create):
			C=str(B.args.get('kind')).upper()
			if C in(D,E,_E):
				A=B
				while isinstance(A.this,exp.Expression):A=A.this
				if A.args.get(_C):F=A.this if C==D else query.database;G=A.this if C==E else _D;H=A.this if C==_E else _D;I=F,G,H;State.identifier_overrides.entries.append(I)
		return B
class ReplaceIdentifierFunction(QueryProcessor):
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.Func)and str(A.this).upper()=='IDENTIFIER'and A.expressions:B=A.expressions[0].copy();B.args['is_string']=_B;return B
		return A
	def get_priority(A):return 100
class InsertCreateTablePlaceholder(QueryProcessor):
	def transform_query(C,expression,query):
		A=expression
		if not is_create_table_expression(A):return A
		if isinstance(A.this.this,exp.Placeholder)or str(A.this.this)=='?':A=A.copy();B=query.params.pop(0);A.this.args[_A]=exp.Identifier(this=B,quoted=_B)
		return A
	def get_priority(A):return ReplaceIdentifierFunction().get_priority()-1
class ReplaceQuestionMarkPlaceholder(QueryProcessor):
	def transform_query(B,expression,**C):
		A=expression
		if isinstance(A,exp.Placeholder):return exp.Literal(this='%s',is_string=_B)
		return A
	def get_priority(A):return InsertCreateTablePlaceholder().get_priority()-1
class HandleDollarReferences(QueryProcessor):
	def transform_query(G,expression,**H):
		A=expression
		if not isinstance(A,exp.Select):return A
		D=list(A.find_all(exp.Parameter))
		if not D:return A
		C=A.find(exp.From)
		if not C:return A
		if not C.this.alias:C.this.args['alias']=E=exp.TableAlias();E.args[_A]='_tmp';E.args['columns']=[]
		F=[]
		for B in D:
			if hasattr(B.this,_A)and is_number(str(B.this.this)):F.append(B)
		for B in F:B.replace(exp.Identifier(this=f"_col{B.this.this}"))
		return A
class ConvertIdentifiersToUpper(QueryProcessor):
	def transform_query(I,expression,**J):
		A=expression
		if not config.CONVERT_NAME_CASING:return A
		if isinstance(A,exp.UserDefinedFunction)and isinstance(A.this,exp.Dot):
			if isinstance(A.this.this,str):A.this.args[_A]=get_canonical_name(A.this.this);return A
		if isinstance(A,exp.Anonymous):F=getattr(A.this,_A,A.this);C=get_canonical_name(str(F));G=C.lower()not in INTERNAL_IDENTIFIERS;A.args[_A]=exp.Identifier(this=C,quoted=G);return A
		if isinstance(A,exp.Kwarg)and isinstance(A.this,exp.Var):H=get_canonical_name(str(A.this.this));A.this.args[_A]=H;return A
		if not isinstance(A,exp.Identifier):return A
		if'information_schema.'in str(A.parent_select).lower():return A
		if A.quoted:return A
		B=A.parent
		if isinstance(B,exp.LanguageProperty):return A
		if isinstance(B,exp.ColumnDef)and A==B.args.get('kind'):return A
		if isinstance(B,exp.Schema)and A in B.expressions and A.find_ancestor(exp.Drop):return A
		D=str(A.this)
		if'.'in D:return A
		A=A.copy();E=get_canonical_name(D,quoted=_B);A.args[_A]=E;A.args[_C]=E.lower()not in INTERNAL_IDENTIFIERS;return A
	def get_priority(G):from snowflake_local.engine.processors.aliases import AddColumnNamesToTableAliases as A;from snowflake_local.engine.processors.arrays import ConvertArrayConstructor as B,ConvertArrayFunctionArgTypes as C;from snowflake_local.engine.processors.types import ReplaceVariantCastWithToVariant as D;from snowflake_local.engine.processors.variants import ReplaceObjectConstruct as E;F=[A().get_priority(),E().get_priority(),C().get_priority(),B().get_priority(),ReplaceQuestionMarkPlaceholder().get_priority(),D().get_priority()];return min(F)-1
class ReplaceDbReferences(QueryProcessor):
	def transform_query(F,expression,query):
		E='catalog';C=query;A=expression;B=A.args.get(E)
		if isinstance(A,exp.Table)and A.args.get('db')and B:
			C.database=B.this
			if not B.quoted:C.database=get_canonical_name(B.this,quoted=_B,type=NameType.DATABASE)
			A.args[E]=_D
		if isinstance(A,exp.UserDefinedFunction):
			D=str(A.this).split('.')
			if len(D)==3:A.this.args[_A]=D[1];C.database=get_canonical_name(D[0],quoted=_B,type=NameType.DATABASE)
		return A
class UpdateFunctionLanguageIdentifier(QueryProcessor):
	def transform_query(Q,expression,**R):
		L='python';A=expression;M={_G:'plv8',L:'plpython3u'}
		if isinstance(A,exp.Create)and isinstance(A.this,exp.UserDefinedFunction):
			E=A.args[_F];C=E.expressions;B=[A for A in C if isinstance(A,exp.LanguageProperty)]
			if not B:F=exp.LanguageProperty();F.args[_A]='SQL';C.append(F);return A
			G=str(B[0].this).lower();N=G==L
			for(O,H)in M.items():
				if G!=O:continue
				if isinstance(B[0].this,exp.Identifier):B[0].this.args[_A]=H
				else:B[0].args[_A]=H
			I=[];J=[A for A in C if str(A.this).lower()=='handler']
			for K in C:
				if isinstance(K,(exp.LanguageProperty,exp.ReturnsProperty)):I.append(K)
			E.args['expressions']=I
			if N and J:P=J[0].args['value'].this;D=textwrap.dedent(A.expression.this);D=D+f"\nreturn {P}(*args)";A.expression.args[_A]=D
		return A
class UpdateIdentifiersInSqlFunctionCode(QueryProcessor):
	def transform_query(G,expression,**H):
		A=expression
		if not isinstance(A,exp.Create)or not isinstance(A.this,exp.UserDefinedFunction):return A
		E=A.args[_F];F=E.expressions;C=[A for A in F if isinstance(A,exp.LanguageProperty)]
		if not C or str(C[0].this).upper()!='SQL':return A
		if not A.expression:return A
		D=str(A.expression)
		if isinstance(A.expression,(exp.Literal,exp.RawString)):D=A.expression.this
		B=Query(query=D);B=apply_query_transforms(B);A.expression.args[_A]=B.query;return A
	def get_priority(A):return UpdateFunctionLanguageIdentifier().get_priority()-1
class ConvertFunctionArgsToLowercase(QueryProcessor):
	def transform_query(H,expression,**I):
		A=expression
		if config.CONVERT_NAME_CASING:return A
		if not isinstance(A,exp.Create):return A
		if not isinstance(A.this,exp.UserDefinedFunction):return A
		D=A.args[_F].expressions;B=[A for A in D if isinstance(A,exp.LanguageProperty)];B=str(B[0].this).lower()if B else _D
		if B not in(_G,'plv8'):return A
		E=[A for A in A.this.expressions if isinstance(A,exp.ColumnDef)]
		for F in E:
			if not A.expression:continue
			C=str(F.this);G=A.expression.this;A.expression.args[_A]=G.replace(C.upper(),C.lower())
		return A
class RemoveTableFuncWrapper(QueryProcessor):
	def transform_query(D,expression,**E):
		B=expression
		if isinstance(B,exp.Table):
			A=B.this;C=A
			if hasattr(A,_A):C=A.this
			if str(C).upper()==_E and A.expressions:return A.expressions[0]
		return B
	def get_priority(A):return 10
class RenameReservedKeywordFunctions(QueryProcessor):
	def transform_query(E,expression,**F):
		A=expression
		if isinstance(A,exp.Func)and isinstance(A.this,str):
			B={'current_role':'get_current_role'}
			for(C,D)in B.items():
				if str(A.this).lower()==C:A.args[_A]=D
		return A
class AdjustCasingOfTableRefs(QueryProcessor):
	def transform_query(D,expression,query):
		A=expression
		if isinstance(A,exp.From):
			B=A.this
			if isinstance(B,exp.Expression)and B.args.get('db'):
				C=B.args['db']
				if C.args.get(_C):C.args[_C]=_B
		return A
class UnwrapTableNamesInBraces(QueryProcessor):
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.From)and isinstance(A.this,exp.Subquery):
			if isinstance(A.this.this,exp.Table):A.args[_A]=A.this.this
		return A