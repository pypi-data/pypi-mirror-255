_Z='COLUMN_DEFAULT'
_Y='DATA_TYPE'
_X='COLUMN_NAME'
_W='description'
_V='expressions'
_U='properties'
_T='ALTER'
_S='TABLE'
_R='null'
_Q=True
_P='expression'
_O='length'
_N='nullable'
_M='scale'
_L='precision'
_K='comment'
_J='SELECT NULL'
_I=False
_H='type'
_G='TEXT'
_F='default'
_E='postgres'
_D='kind'
_C=None
_B='name'
_A='text'
import json,re
from sqlglot import exp,parse_one
from snowflake_local.engine.db_engine import DBEngine,get_db_engine
from snowflake_local.engine.models import Query,StatementType
from snowflake_local.engine.postgres.constants import DEFAULT_DATABASE
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import NameType,get_canonical_name,get_database_from_drop_query,get_table_from_drop_query,is_create_table_expression
from snowflake_local.server.models import QueryResponse
from snowflake_local.utils.queries import QueryHelpers
from snowflake_local.utils.strings import parse_comma_separated_variable_assignments
class HandleShowParameters(QueryProcessor):
	REGEX=re.compile('^\\s*SHOW\\s+PARAMETERS',flags=re.I);SUPPORTED_PARAMS={'AUTOCOMMIT':{_F:'true'},'TIMEZONE':{_F:'America/Los_Angeles'},'TIMESTAMP_NTZ_OUTPUT_FORMAT':{_F:'YYYY-MM-DD HH24:MI:SS.FF3'},'TIMESTAMP_LTZ_OUTPUT_FORMAT':{},'TIMESTAMP_TZ_OUTPUT_FORMAT':{}}
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.Command)and str(A.this).upper()=='SHOW':
			B=str(A.args.get(_P)).strip().lower()
			if B.startswith('parameters'):return parse_one(_J,read=_E)
		return A
	def postprocess_result(G,query,result):
		C=result;B=query;H={'key':_G,'value':_G,_F:_G,'level':_G,_W:_G};C.data.rowtype=[]
		for(I,J)in H.items():C.data.rowtype.append({_B:I,_L:_C,_M:_C,_H:J,_N:_Q,_O:_C})
		C.data.rowset=[]
		for(A,K)in G.SUPPORTED_PARAMS.items():
			F=K.get(_F,'');D='';E=F
			if A in B.session.system_state.parameters:E=B.session.system_state.parameters[A];D='SYSTEM'
			if A in B.session.parameters:E=B.session.parameters[A];D='SESSION'
			L=A,E,F,D,'test description ...';C.data.rowset.append(L)
class HandleShowObjects(QueryProcessor):
	def transform_query(E,expression,query):
		C=query;A=expression
		if isinstance(A,exp.Show)and str(A.this).upper()=='OBJECTS':
			C='SELECT * FROM information_schema.tables';B=A.args.get('scope')
			if isinstance(B,exp.Table):
				if B.this.this:
					D=str(B.this.this)
					if not B.this.quoted:D=get_canonical_name(D,quoted=_I)
					C+=f" WHERE \"table_schema\" = '{D}'"
			return parse_one(C,dialect=_E)
		return A
	def get_priority(A):return ReplaceShowEntities().get_priority()+1
class HandleAlterSession(QueryProcessor):
	REGEX=re.compile('^\\s*ALTER\\s+SESSION\\s+SET\\s+(.+)',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Command)and str(A.this).upper()==_T:
			D=str(A.args.get(_P)).strip().lower()
			if D.startswith('session'):
				C=B.REGEX.match(str(A).replace('\n',''))
				if C:B._set_parameters(query,C.group(1))
				return parse_one(_J,read=_E)
		return A
	def _set_parameters(E,query,expression):
		B=parse_comma_separated_variable_assignments(expression)
		for(A,C)in B.items():
			A=A.strip().upper();D=HandleShowParameters.SUPPORTED_PARAMS.get(A)
			if D is _C:return
			query.session.parameters[A]=C
class HandleShowKeys(QueryProcessor):
	REGEX=re.compile('^\\s*SHOW\\s+(IMPORTED\\s+)?KEYS(\\s+.+)?',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,(exp.Command,exp.Show)):return parse_one(_J,read=_E)
		return A
class HandleShowProcedures(QueryProcessor):
	REGEX=re.compile('^\\s*SHOW\\s+PROCEDURES(\\s+.+)?',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,(exp.Command,exp.Show)):return parse_one(_J,read=_E)
		return A
class FixShowEntitiesResult(QueryProcessor):
	def should_apply(A,query):B=query;return A._is_show_tables(B)or A._is_show_schemas(B)or A._is_show_objects(B)or A._is_show_columns(B)or A._is_show_primary_keys(B)or A._is_show_procedures(B)or A._is_show_imported_keys(B)
	def _is_show_tables(B,query):A=query.original_query;return bool(re.match('^\\s*SHOW\\s+.*TABLES',A,flags=re.I)or re.search('\\s+FROM\\s+information_schema\\s*\\.\\s*tables\\s+',A,flags=re.I))
	def _is_show_schemas(B,query):A=query.original_query;return bool(re.match('^\\s*SHOW\\s+.*SCHEMAS',A,flags=re.I)or re.search('\\s+FROM\\s+information_schema\\s*\\.\\s*schemata\\s+',A,flags=re.I))
	def _is_show_objects(A,query):return bool(re.match('^\\s*SHOW\\s+.*OBJECTS',query.original_query,flags=re.I))
	def _is_show_columns(B,query):A=query.original_query;return bool(re.match('^\\s*SHOW\\s+.*COLUMNS',A,flags=re.I)or re.search('\\s+FROM\\s+information_schema\\s*\\.\\s*columns\\s+',A,flags=re.I))
	def _is_show_primary_keys(A,query):return bool(re.match('^\\s*SHOW\\s+.*PRIMARY\\s+KEYS',query.original_query,flags=re.I))
	def _is_show_imported_keys(A,query):return bool(re.match('^\\s*SHOW\\s+IMPORTED\\s+KEYS',query.original_query,flags=re.I))
	def _is_show_procedures(A,query):return bool(re.match('^\\s*SHOW\\s+PROCEDURES',query.original_query,flags=re.I))
	def postprocess_result(I,query,result):
		m='rely';l='key_sequence';k='options';j='catalog_name';i='TABLE_NAME';X='bytes';W='rows';V='cluster_by';S='budget';R='owner_role_type';Q='retention_time';P='owner';O='column_name';N='table_name';L='data_type';J='integer';H='created_on';G='timestamp_ltz';F=query;D='database_name';C='schema_name';B=result;from snowflake_local.engine.postgres.db_engine_postgres import State,convert_pg_to_snowflake_type as n;Y=I._is_show_objects(F);Z=I._is_show_tables(F);o=I._is_show_schemas(F);p=I._is_show_columns(F);q=I._is_show_procedures(F);r=I._is_show_primary_keys(F);s=I._is_show_imported_keys(F);t=re.match('.+\\sTERSE\\s',F.original_query,flags=re.I);_replace_dict_value(B.data.rowtype,_B,'TABLE_SCHEMA',C);_replace_dict_value(B.data.rowtype,_B,'SCHEMA_NAME',_B)
		if Z or Y:_replace_dict_value(B.data.rowtype,_B,i,_B)
		else:_replace_dict_value(B.data.rowtype,_B,i,N)
		_replace_dict_value(B.data.rowtype,_B,_X,O);_replace_dict_value(B.data.rowtype,_B,'TABLE_TYPE',_D);_replace_dict_value(B.data.rowtype,_B,'TABLE_CATALOG',D);_replace_dict_value(B.data.rowtype,_B,'CATALOG_NAME',D);_replace_dict_value(B.data.rowtype,_B,_Y,L);_replace_dict_value(B.data.rowtype,_B,_Z,_F);_replace_dict_value(B.data.rowtype,_B,'SPECIFIC_CATALOG',j);_replace_dict_value(B.data.rowtype,_B,'SPECIFIC_SCHEMA',C);_replace_dict_value(B.data.rowtype,_B,'SPECIFIC_NAME',_B);M=[];K=[A[_B]for A in B.data.rowtype]
		for T in B.data.rowset:A=dict(zip(K,T));M.append(A)
		def u(_name,_type):A=_type;return{_B:_name,_L:_C,_M:3 if A==G else _C,_H:A,_N:_Q,_O:_C}
		v={H:G,_B:_A,_D:_A,D:_A,C:_A};w={H:G,_B:_A,D:_A,C:_A,_D:_A,_K:_A,V:_A,W:J,X:J,P:_A,Q:_A,R:_A,S:_A};x={H:G,_B:_A,D:_A,C:_A,_D:_A,_K:_A,V:_A,W:J,X:J,P:_A,Q:_A,'automatic_clustering':_A,'change_tracking':_A,'is_external':_A,'enable_schema_evolution':_A,R:_A,'is_event':_A,S:_A};y={H:G,_B:_A,'is_default':_A,'is_current':_A,D:_A,P:_A,_K:_A,k:_A,Q:_A,R:_A,S:_A};z={N:_A,C:_A,O:_A,L:_A,'null?':_A,_F:_A,_D:_A,_P:_A,_K:_A,D:_A,'autoincrement':_A};A0={H:G,D:_A,C:_A,N:_A,O:_A,l:_A,'constraint_name':_A,m:_A,_K:_A};A1={H:G,'pk_database_name':_A,'pk_schema_name':_A,'pk_table_name':_A,'pk_column_name':_A,'fk_database_name':_A,'fk_schema_name':_A,'fk_table_name':_A,'fk_column_name':_A,l:_A,'update_rule':_A,'delete_rule':_A,'fk_name':_A,'pk_name':_A,'deferrability':_A,m:_A,_K:_A};A2={H:G,_B:_A,C:_A,'is_builtin':_A,'is_aggregate':_A,'is_ansi':_A,'min_num_arguments':J,'max_num_arguments':J,'arguments':_A,_W:_A,j:_A,'is_table_function':_A,'valid_for_clustering':_A,'is_secure':_A};E=_C
		if r:E=A0
		elif t:E=v
		elif o:E=y
		elif Y:E=w
		elif Z:E=x
		elif p:E=z
		elif q:E=A2
		elif s:E=A1
		del B.data.rowtype[:];K=[A[_B]for A in B.data.rowtype]
		for(a,A3)in E.items():
			if a in K:continue
			B.data.rowtype.append(u(a,A3))
		for A in M:
			A.setdefault(V,'');A.setdefault(W,0);A.setdefault(X,0);A.setdefault(k,'')
			if A.get(_F)is _C:A[_F]=''
			if A.get(L):A4=n(A[L]);A[L]=json.dumps({_H:A4})
			A.setdefault(_K,'');A.setdefault(P,'PUBLIC');A.setdefault(Q,'1');A.setdefault(R,'ROLE');A.setdefault(S,_C)
			if A.get(_D)=='BASE TABLE':A[_D]=_S
			A.setdefault(H,'0')
		for A in M:
			for U in(_B,C,D,N,O):
				if A.get(U):A[U]=A[U].upper()
			b=A.get(D);c=A.get(C);d=A.get(_B)
			if any((b,c,d)):
				e=State.identifier_overrides.find_match(b,schema=c,obj_name=d)
				if e:
					f,g,h=e
					if h:A[_B]=h
					elif g:A[C]=g
					elif f:A[D]=f
		K=[A[_B]for A in B.data.rowtype];B.data.rowset=[]
		for A in M:T=[A.get(B)for B in K];B.data.rowset.append(T)
class GetAvailableSchemas(QueryProcessor):
	def transform_query(H,expression,query):
		B=query;A=expression
		if isinstance(A,exp.Func)and str(A.this).lower()=='current_schemas':
			C=try_get_db_engine()
			if C:D=Query(query='SELECT schema_name FROM information_schema.schemata',database=B.database);E=B.database or DEFAULT_DATABASE;F=C.execute_query(D);G=[f"{E}.{A[0]}".upper()for A in F.rows];return exp.Literal(this=json.dumps(G),is_string=_Q)
		return A
class ConvertDescribeTableResultColumns(QueryProcessor):
	DESCRIBE_TABLE_COL_ATTRS={_B:_X,_H:_Y,_D:"'COLUMN'",'null?':'IS_NULLABLE',_F:_Z,'primary key':"'N'",'unique key':"'N'",'check':_R,_P:_R,_K:_R,'policy name':_R,'privacy domain':_R}
	def should_apply(D,query):A=query.original_query;B=re.match('^DESC(RIBE)?\\s+(?!FILE\\s+FORMAT\\s+).+',A,flags=re.I);C=re.match('\\s+information_schema\\s*\\.\\s*columns\\s+',A,flags=re.I);return bool(B or C)
	def postprocess_result(E,query,result):
		A=result;G=[A[_B]for A in A.data.rowtype];F=list(E.DESCRIBE_TABLE_COL_ATTRS);A.data.rowtype=[]
		for H in F:A.data.rowtype.append({_B:H,_L:_C,_M:_C,_H:'VARCHAR',_N:_Q,_O:_C})
		for(I,J)in enumerate(A.data.rowset):
			B=[]
			for K in F:
				C=E.DESCRIBE_TABLE_COL_ATTRS[K]
				if C.startswith("'"):B.append(C.strip("'"))
				elif C==_R:B.append(_C)
				else:L=dict(zip(G,J));D=L[C];D={'YES':'Y','NO':'N'}.get(D)or D;B.append(D)
			A.data.rowset[I]=B
class ReturnDescribeTableError(QueryProcessor):
	def postprocess_result(C,query,result):
		A=result;B=re.match('DESC(?:RIBE)?\\s+(?!FILE\\s+FORMAT\\s+).+',query.original_query,flags=re.I)
		if B and not A.data.rowset:A.success=_I
class HandleDropDatabase(QueryProcessor):
	def should_apply(A,query):return bool(get_database_from_drop_query(query.original_query))
	def postprocess_result(C,query,result):A=query;B=get_database_from_drop_query(A.original_query);State.initialized_dbs=[A for A in State.initialized_dbs if A.lower()!=B.lower()];A.session.database=_C;A.session.schema=_C
class FixDropTableResult(QueryProcessor):
	def should_apply(A,query):return bool(get_table_from_drop_query(query.original_query))
	def postprocess_result(C,query,result):A=result;B=get_table_from_drop_query(query.original_query);A.data.rowset.append([f"{B} successfully dropped."]);A.data.rowtype.append({_B:'status',_H:_A,_O:0,_L:0,_M:0,_N:_Q})
class ReturnInsertedItems(QueryProcessor):
	def transform_query(B,expression,**C):
		A=expression
		if isinstance(A,exp.Insert):A.args['returning']=' RETURNING 1'
		return A
class RemoveIfNotExists(QueryProcessor):
	def transform_query(D,expression,**E):
		C='exists';A=expression
		if not isinstance(A,exp.Create):return A
		B=A.copy()
		if B.args.get(C):B.args[C]=_I
		return B
class RemoveCreateOrReplace(QueryProcessor):
	def transform_query(L,expression,query):
		I='replace';F=query;A=expression
		if not isinstance(A,exp.Create):return A
		G=try_get_db_engine()
		if A.args.get(I):
			D=A.copy();D.args[I]=_I;H=str(D.args.get(_D)).upper()
			if G and H in(_S,'FUNCTION'):
				B=str(D.this.this);C=B.split('.')
				if len(C)>=2:J=get_canonical_name(C[-2]);K=get_canonical_name(C[-1]);B=f"{J}.{K}"
				else:B=get_canonical_name(B)
				E=Query(query=f"DROP {H} IF EXISTS {B}");E.session=F.session;E.database=F.database
				if len(C)>=3:E.database=get_canonical_name(C[0],quoted=_I,type=NameType.DATABASE)
				G.execute_query(E)
			return D
		return A
class RemoveTransientKeyword(QueryProcessor):
	def transform_query(E,expression,**F):
		B=expression
		if not is_create_table_expression(B):return B
		C=B.copy();A=C.args[_U]
		if A:
			if hasattr(A,_V):A=A.expressions
			D=exp.TransientProperty()
			if D in A:A.remove(D)
		return C
class ReplaceUnknownUserConfigParams(QueryProcessor):
	def transform_query(E,expression,**F):
		A=expression
		if isinstance(A,exp.Command)and str(A.this).upper()==_T:
			C=str(A.expression).strip();D='\\s*USER\\s+\\w+\\s+SET\\s+\\w+\\s*=\\s*[\'\\"]?(.*?)[\'\\"]?\\s*$';B=re.match(D,C,flags=re.I)
			if B:return parse_one(f"SELECT '{B.group(1)}'")
		return A
class ReplaceCreateSchema(QueryProcessor):
	def transform_query(C,expression,query):
		A=expression
		if not isinstance(A,exp.Create):return A
		A=A.copy();B=A.args.get(_D)
		if str(B).upper()=='SCHEMA':query.database=get_canonical_name(A.this.db,quoted=_I,type=NameType.DATABASE);A.this.args['db']=_C
		return A
class ReplaceShowEntities(QueryProcessor):
	def transform_query(N,expression,**O):
		G='columns';E='tables';B=expression
		if not isinstance(B,(exp.Command,exp.Show)):return B
		A=''
		if isinstance(B,exp.Command):
			H=str(B.this).upper()
			if H!='SHOW':return B
			A=str(B.args.get(_P)).strip().lower()
		elif isinstance(B,exp.Show):A=str(B.this).strip().lower()
		A=A.removeprefix('terse').strip()
		if A.startswith('primary keys'):I='\n            SELECT a.attname as column_name, format_type(a.atttypid, a.atttypmod) AS data_type, c.relname AS table_name\n            FROM   pg_index i\n            JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)\n            JOIN   pg_class as c ON c.oid = i.indrelid\n            WHERE  i.indisprimary;\n            ';return parse_one(I,read=_E)
		if A.startswith('imported keys'):return parse_one(_J,read=_E)
		D=[];J='^\\s*\\S+\\s+(\\S+)\\.(\\S+)(.*)';F=re.match(J,A)
		if F:D.append(f"table_schema = '{F.group(2)}'")
		if A.startswith(E):C=E
		elif A.startswith('schemas'):C='schemata'
		elif A.startswith('objects'):C=E
		elif A.startswith(G):C=G
		elif A.startswith('procedures'):C='routines';D.append("specific_schema <> 'pg_catalog'")
		else:return B
		K=f"WHERE {' AND '.join(A for A in D)}"if D else'';L=f"SELECT * FROM information_schema.{C} {K}";M=parse_one(L,read=_E);return M
class RemoveTableClusterBy(QueryProcessor):
	def transform_query(F,expression,**G):
		A=expression
		if is_create_table_expression(A):
			B=A.args[_U]
			if B:D=[A for A in B if not isinstance(A,exp.Cluster)];A.args[_U].args[_V]=D
		elif isinstance(A,exp.Command)and A.this==_T:
			E='(.+)\\s*CLUSTER\\s+BY([\\w\\s,]+)(.*)';C=re.sub(E,'\\1\\3',A.expression,flags=re.I);A.args[_P]=C
			if re.match('\\s*TABLE\\s+\\w+',C,flags=re.I):return parse_one(_J,read=_E)
		elif isinstance(A,exp.AlterTable):
			if re.match('.+\\sCLUSTER\\s+BY\\s+',str(A),flags=re.I):return parse_one(_J,read=_E)
		return A
class ReplaceDescribeTable(QueryProcessor):
	def transform_query(G,expression,**H):
		A=expression
		if not isinstance(A,exp.Describe):return A
		D=A.args.get(_D)or _S
		if str(D).upper()==_S:
			C=A.this.name;B=C
			if not C:B='?'
			elif not A.this.this.args.get('quoted'):B=get_canonical_name(C,quoted=_I)
			if B!='?':B=f"'{B}'"
			E=f"SELECT * FROM information_schema.columns WHERE table_name={B}";F=parse_one(E,read=_E);return F
		return A
class HandleShowPackages(QueryProcessor):
	REGEX=re.compile('.+FROM\\s+information_schema\\s*\\.\\s*packages',flags=re.I)
	def should_apply(A,query):return bool(A.REGEX.match(query.original_query))
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Select):return parse_one(_J,read=_E)
		return A
	def postprocess_result(F,query,result):
		A=result;B=[['lib-name','lib-version','python',_C]];A.data.rowset=B;A.data.rowtype=[];C={'PACKAGE_NAME':_G,'VERSION':_G,'LANGUAGE':_G,'DETAILS':_G}
		for(D,E)in C.items():A.data.rowtype.append({_B:D,_L:_C,_M:_C,_H:E,_N:_Q,_O:_C})
class FixColumnsForCTAS(QueryProcessor):
	def transform_query(C,expression,query):
		A=expression
		if isinstance(A,exp.Create)and str(A.args.get(_D)).upper()==_S and isinstance(A.expression,exp.Select)and isinstance(A.this,exp.Schema):
			for B in A.this.expressions:
				if isinstance(B,exp.ColumnDef):B.args.pop(_D,_C)
		return A
class FixResultForDescribeOnly(QueryProcessor):
	def postprocess_result(B,query,result):
		A=query.request or{}
		if A.get('describeOnly'):result.data.rowset=[]
class AdjustResultsForUpdateQueries(QueryProcessor):
	def should_apply(A,query):return QueryHelpers.is_update_query(query.original_query)
	def postprocess_result(J,query,result):G='fixed';F='collation';E='byteLength';D='table';C='schema';B='database';A=result;from snowflake_local.engine.session import APP_STATE as H;A.data.rowtype=[{_B:'number of rows updated',B:'',C:'',D:'',_L:19,E:_C,_H:G,_M:0,_N:_I,F:_C,_O:_C},{_B:'number of multi-joined rows updated',B:'',C:'',D:'',_L:19,E:_C,_H:G,_M:0,_N:_I,F:_C,_O:_C}];I=H.queries[query.query_id];A.data.rowset=[[str(I.result.row_count),'0']]
class UpdateStatementTypeIdInResponse(QueryProcessor):
	def postprocess_result(C,query,result):
		B=query;A=result
		if A.data.statementTypeId:return
		if QueryHelpers.is_update_query(B.original_query):A.data.statementTypeId=StatementType.UPDATE.value
		if QueryHelpers.is_describe_query(B.original_query):A.data.statementTypeId=StatementType.DESCRIBE.value
class RemoveCommentFromCreateQueries(QueryProcessor):
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Properties)and A.find_ancestor(exp.Create):A.args[_V]=[A for A in A.expressions if not isinstance(A,exp.SchemaCommentProperty)]
		return A
def _replace_dict_value(values,attr_key,attr_value,attr_value_replace):
	A=attr_key;B=[B for B in values if B[A]==attr_value]
	if B:B[0][A]=attr_value_replace
def try_get_db_engine():
	try:return get_db_engine()
	except ImportError:return