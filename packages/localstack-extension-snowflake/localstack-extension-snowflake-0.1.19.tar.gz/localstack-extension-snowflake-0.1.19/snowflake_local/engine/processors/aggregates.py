_F='array_agg_ordered'
_E='values'
_D='this'
_C=True
_B='separator'
_A=None
import json
from typing import Any,Callable
from localstack.utils.collections import ensure_list
from localstack.utils.json import json_safe
from sqlglot import exp
from snowflake_local.engine.models import AGG_COMPARABLE_TYPE,VARIANT
from snowflake_local.engine.postgres.constants import BASIC_TYPES,PG_VARIANT_TYPE
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import get_canonical_name,to_variant,unwrap_variant_type
class CastParamsForStringAgg(QueryProcessor):
	def transform_query(L,expression,**M):
		E='expressions';A=expression
		if not isinstance(A,exp.GroupConcat):return A
		B=''
		def H(expr):
			C=expr;nonlocal B;D=C.this;A=C
			if isinstance(D,exp.Distinct):D=C.this.expressions[0];A=C.this.expressions
			if not isinstance(D,exp.Cast):
				E=exp.Cast();E.args[_D]=D;E.args['to']=exp.DataType.build('TEXT')
				if isinstance(A,list):
					A[0]=E
					if len(A)>1:F=A.pop(1);B=str(F.this)
				else:A.args[_D]=E
		H(A)
		if A.args.get(_B)is _A:A.args[_B]=exp.Literal(this=B,is_string=_C)
		if not A.parent_select:return A
		F=isinstance(A.this,exp.Distinct)
		if F:
			G=A.parent_select.find(exp.WithinGroup)
			if G:
				if len(A.this.expressions)!=1:raise Exception(f"Expected a single DISTINCT clause in combination with WITHIN GROUP, got: {A.this.expressions}")
				if isinstance(G.this,exp.GroupConcat):
					I='STRING_AGG_ORDERED_DISTINCT'if F else'STRING_AGG_ORDERED';C=exp.Anonymous(this=I,expressions=G.this.expressions)
					if B:C.args[E]=[exp.Literal(this=B,is_string=_C)]
					return C
		if not B and A.args.get(_B):B=A.args[_B].this
		J='STRING_AGG_NOGROUP_DISTINCT'if F else'STRING_AGG_NOGROUP';C=exp.Anonymous(this=J,expressions=ensure_list(A.this))
		if isinstance(C.args[E][0],exp.Distinct):
			D=C.args[E][0].expressions
			if isinstance(D,list)and len(D)==1:D=D[0]
			C.args[E][0]=D
		if B:K=exp.Literal(this=B,is_string=_C);C.args[E]+=[K]
		return C
class ConvertArrayAggParams(QueryProcessor):
	def transform_query(G,expression,**H):
		F='from';D='alias';B=expression
		if not isinstance(B,exp.Select):return B
		C=[A for A in B.expressions if isinstance(A,exp.WithinGroup)];A=_A
		if C:
			if isinstance(C[0].this,exp.ArrayAgg):C[0].args[_D]=f"{get_canonical_name(_F)}()";A=B.args.get(F)
		else:
			E=[A for A in B.expressions if isinstance(A,exp.ArrayAgg)]
			if E:
				A=B.args.get(F)
				if isinstance(A.this,exp.Values)and not A.this.args.get(D):E[0].args[_D]='_tmp_col1'
		if A and isinstance(A.this,exp.Values)and not A.this.args.get(D):A.this.args[D]='_tmp_table(_tmp_col1)'
		return B
class HandleArrayUnionAgg(QueryProcessor):
	def initialize_db_resources(E,database):B='array_union_agg_finalize';A='array_union_agg_aggregate';C=State.server;D=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)}
                (_result {PG_VARIANT_TYPE}, _input {PG_VARIANT_TYPE}) RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.aggregates import HandleArrayUnionAgg
                return HandleArrayUnionAgg.array_union_agg_aggregate(_result, _input)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(B)}
                (_result {PG_VARIANT_TYPE}) RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.aggregates import HandleArrayUnionAgg
                return HandleArrayUnionAgg.array_union_agg_finalize(_result)
            $$;
            CREATE AGGREGATE {get_canonical_name("array_union_agg")} ({PG_VARIANT_TYPE}) (
                STYPE = TEXT,
                SFUNC = {get_canonical_name(A)},
                FINALFUNC = {get_canonical_name(B)}
            )
        """;C.run_query(D,database=database)
	@classmethod
	def array_union_agg_aggregate(D,_result,_input):
		C=_result;A=_input;B=[]
		if C:B=unwrap_variant_type(C,expected_type=list)
		A=unwrap_variant_type(A);B.append(A);return to_variant(B)
	@classmethod
	def array_union_agg_finalize(J,_result):
		D=_result;D=unwrap_variant_type(D);E=[]
		for I in D:
			F=[]
			for G in I:
				A=_A
				for B in F:
					if B[0]==G:A=B;break
				if A:A.append(G)
				else:F.append([G])
			for C in F:
				A=_A
				for B in E:
					if B[0]==C[0]:A=B;break
				if A:
					if len(C)>len(A):A.clear();A.extend(C)
				else:E.append(C)
		H=[]
		for B in E:H.extend(B)
		return to_variant(H)
class HandleArgMinMax(QueryProcessor):
	def initialize_db_resources(J,database):
		H='TIMESTAMP';G='NUMERIC';I=State.server;B=[]
		for A in('arg_min','arg_max'):
			for(E,C)in enumerate((G,'TEXT',H)):
				B.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name(f"{A}_finalize_{E}")} (
                   _result TEXT[]
                ) RETURNS {C} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.aggregates import HandleArgMinMax
                    return HandleArgMinMax.arg_min_max_finalize(_result)
                $$
                """)
				for F in(G,H):D=f"""
                    CREATE OR REPLACE FUNCTION {get_canonical_name(f"{A}_aggregate")} (
                       _result TEXT[],
                       _input1 {C},
                       _input2 {F}
                    ) RETURNS TEXT[] LANGUAGE plpython3u IMMUTABLE AS $$
                        from snowflake_local.engine.processors.aggregates import HandleArgMinMax
                        return HandleArgMinMax.{A}_aggregate(_result, _input1, _input2)
                    $$;
                    CREATE AGGREGATE {get_canonical_name(A)} ({C}, {F}) (
                        INITCOND = '{{null,null}}',
                        STYPE = TEXT[],
                        SFUNC = {get_canonical_name(f"{A}_aggregate")},
                        FINALFUNC = {get_canonical_name(f"{A}_finalize_{E}")}
                    )
                    """;B.append(D)
		D='; '.join(B);I.run_query(D,database=database)
	@classmethod
	def arg_min_aggregate(A,_result,_input1,_input2):
		def B(val1,val2):return val1<val2
		return A._arg_min_max_aggregate(_result,_input1,_input2,comparator=B)
	@classmethod
	def arg_max_aggregate(A,_result,_input1,_input2):
		def B(val1,val2):return val1>val2
		return A._arg_min_max_aggregate(_result,_input1,_input2,comparator=B)
	@classmethod
	def _arg_min_max_aggregate(F,_result,_input1,_input2,comparator):
		B=_input2;A=_result
		if B is _A:return A
		C=json.dumps(json_safe(_input1));D=json.dumps(json_safe(B))
		if A[1]is _A:return[C,D]
		E=unwrap_variant_type(A[1])
		if comparator(B,E):return[C,D]
		return A
	@classmethod
	def arg_min_max_finalize(B,_result):
		A=_result
		if isinstance(A[0],str):return unwrap_variant_type(A[0])
		return A[0]
class HandleArrayAgg(QueryProcessor):
	def initialize_db_resources(E,database):
		B='array_agg_aggregate';C=[]
		for A in BASIC_TYPES:C.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name(B)}
                (_result TEXT, _input1 {A}) RETURNS TEXT LANGUAGE plpython3u IMMUTABLE
                AS $$
                    from snowflake_local.engine.processors.aggregates import HandleArrayAgg
                    return HandleArrayAgg.array_agg_aggregate(_result, _input1)
                $$;
                CREATE AGGREGATE {get_canonical_name(_F)} (ORDER BY {A}) (
                    STYPE = TEXT,
                    SFUNC = {get_canonical_name(B)}
                );
                CREATE AGGREGATE {get_canonical_name("array_agg")} ({A}) (
                    STYPE = TEXT,
                    SFUNC = {get_canonical_name(B)}
                )
            """)
		D='; '.join(C);State.server.run_query(D,database=database)
	@classmethod
	def array_agg_aggregate(D,_result,_input1):
		C=_input1;B=_result
		if C is _A:return B
		A=unwrap_variant_type(B or'[]');A.append(C);A=to_variant(A);return A
class HandleStringAgg(QueryProcessor):
	def initialize_db_resources(L,database):
		J='string_agg_nogroup_distinct';I='string_agg_nogroup';H='string_agg_ordered_distinct';G='string_agg_ordered';E='string_agg_aggregate_distinct';D='string_agg_aggregate';C='string_agg_aggregate_ordered_finalize';B='string_agg_aggregate_finalize';F=[];F.append(f"""
        CREATE OR REPLACE FUNCTION {get_canonical_name(B)} (
           _result {PG_VARIANT_TYPE}, _separator TEXT) RETURNS {PG_VARIANT_TYPE}
        LANGUAGE plpython3u IMMUTABLE AS $$
            from snowflake_local.engine.processors.aggregates import HandleStringAgg
            return HandleStringAgg.string_agg_aggregate_finalize(_result, _separator)
        $$;
        CREATE OR REPLACE FUNCTION {get_canonical_name(B)} (
           _result {PG_VARIANT_TYPE} ) RETURNS {PG_VARIANT_TYPE}
        LANGUAGE plpython3u IMMUTABLE AS $$
            from snowflake_local.engine.processors.aggregates import HandleStringAgg
            return HandleStringAgg.string_agg_aggregate_finalize(_result)
        $$;
        CREATE OR REPLACE FUNCTION {get_canonical_name(C)} (
           _result {PG_VARIANT_TYPE}, _separator TEXT) RETURNS {PG_VARIANT_TYPE}
        LANGUAGE plpython3u IMMUTABLE AS $$
            from snowflake_local.engine.processors.aggregates import HandleStringAgg
            return HandleStringAgg.string_agg_aggregate_ordered_finalize(_result, _separator)
        $$;
        CREATE OR REPLACE FUNCTION {get_canonical_name(C)} (
           _result {PG_VARIANT_TYPE} ) RETURNS {PG_VARIANT_TYPE}
        LANGUAGE plpython3u IMMUTABLE AS $$
            from snowflake_local.engine.processors.aggregates import HandleStringAgg
            return HandleStringAgg.string_agg_aggregate_ordered_finalize(_result)
        $$;
        """)
		for A in BASIC_TYPES:F.append(f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name(D)}
                    (_result {PG_VARIANT_TYPE}, _input {A})
                RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.aggregates import HandleStringAgg
                    return HandleStringAgg.string_agg_aggregate(_result, _input)
                $$;
                CREATE OR REPLACE FUNCTION {get_canonical_name(D)}
                    (_result {PG_VARIANT_TYPE}, _input {A}, _separator TEXT)
                RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.aggregates import HandleStringAgg
                    return HandleStringAgg.string_agg_aggregate(_result, _input, _separator)
                $$;
                CREATE OR REPLACE FUNCTION {get_canonical_name(E)}
                    (_result {PG_VARIANT_TYPE}, _input {A})
                RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.aggregates import HandleStringAgg
                    return HandleStringAgg.string_agg_aggregate_distinct(_result, _input)
                $$;
                CREATE OR REPLACE FUNCTION {get_canonical_name(E)}
                    (_result {PG_VARIANT_TYPE}, _input {A}, _separator TEXT)
                RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.aggregates import HandleStringAgg
                    return HandleStringAgg.string_agg_aggregate_distinct(_result, _input, _separator)
                $$;
                CREATE AGGREGATE {get_canonical_name(G)} (_separator TEXT ORDER BY {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(D)},
                    FINALFUNC = {get_canonical_name(C)}
                );
                CREATE AGGREGATE {get_canonical_name(G)} (ORDER BY {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(D)},
                    FINALFUNC = {get_canonical_name(C)}
                );
                CREATE AGGREGATE {get_canonical_name(H)} (_separator TEXT ORDER BY {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(E)},
                    FINALFUNC = {get_canonical_name(C)}
                );
                CREATE AGGREGATE {get_canonical_name(H)} (ORDER BY {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(E)},
                    FINALFUNC = {get_canonical_name(C)}
                );

                CREATE AGGREGATE {get_canonical_name(I)} (_value {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(D)},
                    FINALFUNC = {get_canonical_name(B)}
                );
                CREATE AGGREGATE {get_canonical_name(I)} (_value {A}, _separator TEXT) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(D)},
                    FINALFUNC = {get_canonical_name(B)}
                );
                CREATE AGGREGATE {get_canonical_name(J)} (_value {A}) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(E)},
                    FINALFUNC = {get_canonical_name(B)}
                );
                CREATE AGGREGATE {get_canonical_name(J)} (_value {A}, _separator TEXT) (
                    STYPE = {PG_VARIANT_TYPE},
                    SFUNC = {get_canonical_name(E)},
                    FINALFUNC = {get_canonical_name(B)}
                )""")
		K='; '.join(F);State.server.run_query(K,database=database)
	@classmethod
	def string_agg_aggregate(A,_result,_input,separator=_A):return A.string_agg_aggregate_distinct(_result,_input,separator=separator,distinct=False)
	@classmethod
	def string_agg_aggregate_distinct(E,_result,_input,separator=_A,distinct=_C):
		D=_result;C=separator;B=_input
		if B is _A:return D
		A=unwrap_variant_type(D or'[]')
		if C:
			if isinstance(A,dict):A=A[_E]
		if not distinct or B not in A:A.append(B)
		if C:A={_B:C,_E:A}
		A=to_variant(A);return A
	@classmethod
	def string_agg_aggregate_ordered_finalize(C,_result,separator=_A,sort=_C):
		B=separator;B=B or'';A=unwrap_variant_type(_result)
		if sort:A=sorted(A)
		A=B.join([str(A)for A in A]);return A
	@classmethod
	def string_agg_aggregate_finalize(C,_result,separator=_A):
		B=separator;A=_result;A=unwrap_variant_type(A)
		if isinstance(A,dict)and A.get(_B):B=A[_B];A=A[_E]
		A=to_variant(A);return C.string_agg_aggregate_ordered_finalize(A,separator=B,sort=False)