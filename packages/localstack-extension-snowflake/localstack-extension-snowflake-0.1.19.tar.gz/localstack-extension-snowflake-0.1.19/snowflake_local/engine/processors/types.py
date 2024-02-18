_O='UNKNOWN'
_N='VIEW'
_M='FUNCTION'
_L='TABLE'
_K='nullable'
_J='scale'
_I='precision'
_H='name'
_G='VARIANT'
_F='kind'
_E=False
_D='length'
_C=True
_B='TEXT'
_A='type'
import calendar,datetime,json,re
from sqlglot import exp
from snowflake_local import config
from snowflake_local.engine.models import VARIANT_EXT_MARKER_PREFIX,VARIANT_MARKER_PREFIX,Query,StatementType
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import SNOWFLAKE_FUNCTIONS,get_canonical_name,get_table_from_creation_query,get_view_from_creation_query,is_variant_encoded_value,parse_snowflake_query,remove_variant_prefix,unwrap_variant_type
from snowflake_local.server.models import QueryResponse
from snowflake_local.utils.encodings import to_pyarrow_table_bytes_b64
from snowflake_local.utils.queries import QueryHelpers
TYPE_MAPPINGS={_G:_B,'OBJECT':_B,'STRING':_B,_O:_B,'ARRAY':_B}
class EncodeComplexTypesInResults(QueryProcessor):
	def postprocess_result(D,query,result):
		for A in result.data.rowset:
			for(C,B)in enumerate(A):
				if isinstance(B,(dict,list)):A[C]=json.dumps(B)
class ConvertTimestampResults(QueryProcessor):
	def postprocess_result(L,query,result):
		D=result
		for(E,C)in enumerate(D.data.rowtype):
			B=str(C.get(_A)).upper();F='TIMESTAMP','TIMESTAMP WITHOUT TIME ZONE';G='TIMESTAMP WITH TIME ZONE',;H='DATE',
			if B in F:C[_A]='TIMESTAMP_NTZ'
			if B in G:C[_A]='TIMESTAMP_TZ'
			I=B in H
			if B not in F+G+H:continue
			for J in D.data.rowset:
				A=J[E]
				if I:K=calendar.timegm(A.timetuple());A=datetime.datetime.utcfromtimestamp(K)
				if isinstance(A,datetime.datetime):A=A.replace(tzinfo=datetime.timezone.utc)
				if A is None:continue
				A=int(A.timestamp())
				if I:A=A/24/60/60
				J[E]=str(int(A))
class UnwrapVariantTypes(QueryProcessor):
	def postprocess_result(D,query,result):
		for A in result.data.rowset:
			for(B,C)in enumerate(A):
				if not isinstance(C,str):continue
				if C.startswith(VARIANT_EXT_MARKER_PREFIX):A[B]=remove_variant_prefix(C)
				if C.startswith(VARIANT_MARKER_PREFIX):
					A[B]=unwrap_variant_type(C)
					if isinstance(A[B],(list,dict)):A[B]=json.dumps(A[B])
	def get_priority(A):return AdjustQueryResultFormat().get_priority()-1
class UpdateColumnTypesAsVariant(QueryProcessor):
	def postprocess_result(F,query,result):
		A=result
		if not A.data.rowset:return
		B=A.data.rowset[0]
		for(C,D)in enumerate(A.data.rowtype):
			if is_variant_encoded_value(B[C])and D[_A]==_B:
				D[_A]=_G
				if not is_variant_encoded_value(B[C],external=_C):
					E=unwrap_variant_type(B[C])
					if isinstance(E,list):D[_A]='ARRAY'
	def get_priority(B):A=[ReplaceUnknownTypes().get_priority(),AdjustColumnTypes().get_priority()];return min(A)-1
class FixBooleanResultValues(QueryProcessor):
	def postprocess_result(F,query,result):
		A=result
		for(B,D)in enumerate(A.data.rowtype):
			E=D.get(_A,'')
			if E.upper()not in('BOOL','BOOLEAN'):continue
			for C in A.data.rowset:C[B]='TRUE'if str(C[B]).lower()=='true'else'FALSE'
class AdjustQueryResultFormat(QueryProcessor):
	def postprocess_result(D,query,result):
		A=result
		if not config.RETURN_SELECT_AS_ARROW:return
		B=QueryHelpers.is_select_query(query.original_query);A.data.queryResultFormat='arrow'if B else'json'
		if not B:return
		A.data.statementTypeId=StatementType.SELECT.value
		if not A.data.rowset:return
		def C():
			for B in A.data.rowset:
				for C in B:
					if C is not None:return _E
		if C():return
		A.data.rowsetBase64=to_pyarrow_table_bytes_b64(A);A.data.rowset=[]
	def get_priority(C):from snowflake_local.engine.processors.metadata import FixShowEntitiesResult as A;B=[UpdateColumnTypesAsVariant().get_priority(),A().get_priority()];return min(B)-1
class AdjustColumnTypes(QueryProcessor):
	TYPE_MAPPINGS={_O:_B,'VARCHAR':_B,'CHARACTER VARYING':_B}
	def postprocess_result(C,query,result):
		for A in result.data.rowtype:
			D=A.get(_A,'');B=C.TYPE_MAPPINGS.get(D)
			if B:A[_A]=B
			if A[_A].upper()==_B and A.get(_D)==-1:A[_D]=0
class FixInsertQueryResult(QueryProcessor):
	def should_apply(A,query):return bool(re.match('^\\s*INSERT\\s+.+',query.original_query,flags=re.I))
	def postprocess_result(B,query,result):A=result;A.data.rowset=[[len(A.data.rowset)]];A.data.rowtype=[{_H:'count',_A:'integer',_D:0,_I:0,_J:0,_K:_C}]
class FixCreateEntityResult(QueryProcessor):
	def should_apply(A,query):B=A._get_created_entity_type(query.original_query);return B in(_L,_M,_N)
	def postprocess_result(E,query,result):
		D=result;B=query;C=E._get_created_entity_type(B.original_query);F={_L:'Table',_M:'Function',_N:'View'};G=F.get(C)
		if C==_L:A=get_table_from_creation_query(B.original_query);A=A and A.upper()
		elif C==_M:H=parse_snowflake_query(B.original_query);I=H.this;A=get_canonical_name(str(I.this),quoted=_E)
		elif C==_N:A=get_view_from_creation_query(B.original_query);A=A and get_canonical_name(A,quoted=_E)
		else:A='test'
		D.data.rowset.append([f"{G} {A} successfully created."]);D.data.rowtype.append({_H:'status',_A:'text',_D:0,_I:0,_J:0,_K:_C})
	def _get_created_entity_type(B,query):
		A=parse_snowflake_query(query)
		if isinstance(A,exp.Create):return A.args.get(_F)
class AddDefaultResultIfEmpty(QueryProcessor):
	def should_apply(B,query):
		A=parse_snowflake_query(query.original_query)
		if isinstance(A,exp.AlterTable):return _C
		return isinstance(A,exp.Command)and str(A.this).upper()=='ALTER'
	def postprocess_result(B,query,result):
		A=result
		if not A.data.rowtype:A.data.rowtype=[{_H:'?column?',_A:'text',_D:0,_I:0,_J:0,_K:_C}]
		A.data.rowset=[('Statement executed successfully.',)]
class ReplaceUnknownTypes(QueryProcessor):
	def transform_query(F,expression,**G):
		A=expression
		for(C,D)in TYPE_MAPPINGS.items():
			E=getattr(exp.DataType.Type,D.upper());B=A
			if isinstance(B,exp.Alias):B=B.this
			if isinstance(B,exp.Cast)and B.to==exp.DataType.build(C):B.args['to']=exp.DataType.build(E)
			if isinstance(A,exp.ColumnDef):
				if A.args.get(_F)==exp.DataType.build(C):A.args[_F]=exp.DataType.build(E)
			if isinstance(A,exp.Identifier)and isinstance(A.parent,exp.Schema):
				if str(A.this).upper()==C.upper():A.args['this']=D.upper()
		return A
	def get_priority(A):return ReplaceVariantCastWithToVariant().get_priority()-1
class ReplaceVariantCastWithToVariant(QueryProcessor):
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Cast)and A.to==exp.DataType.build(_G):
			if isinstance(A.parent,exp.Anonymous):
				if str(A.parent.this).lower()not in SNOWFLAKE_FUNCTIONS:return A
			return exp.Anonymous(this='to_variant',expressions=[A.this])
		return A
	def get_priority(B):from snowflake_local.engine.processors.aliases import AddColumnNamesToTableAliases as A;return A().get_priority()-1
class AdjustAutoIncrementColumnTypes(QueryProcessor):
	def transform_query(D,expression,**E):
		A=expression
		if isinstance(A,exp.ColumnDef):
			B=exp.AutoIncrementColumnConstraint,exp.GeneratedAsIdentityColumnConstraint
			for C in A.constraints:
				if isinstance(C.kind,B):A.args[_F]=exp.Identifier(this='SERIAL',quoted=_E)
			A.args['constraints']=[A for A in A.constraints if not isinstance(A.kind,B)]
		return A