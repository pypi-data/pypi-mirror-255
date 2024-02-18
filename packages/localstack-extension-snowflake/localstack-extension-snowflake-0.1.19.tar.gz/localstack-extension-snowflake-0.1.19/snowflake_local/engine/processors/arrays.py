_K='array_insert'
_J='is_array'
_I='array_remove'
_H='array_prepend'
_G='array_cat'
_F='array_append'
_E='array_contains'
_D='array_construct_compact'
_C='array_construct'
_B=True
_A=None
import logging
from functools import cmp_to_key
from typing import Any
from localstack.utils.numbers import is_number
from sqlglot import exp
from snowflake_local.engine.models import VARIANT,Query
from snowflake_local.engine.postgres.constants import PG_VARIANT_TYPE
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import convert_function_args_to_variant,get_canonical_name,to_variant,unwrap_potential_variant_type,unwrap_variant_type
LOG=logging.getLogger(__name__)
class ConvertArrayConstructor(QueryProcessor):
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.Array):B=exp.Anonymous(this='ARRAY_CONSTRUCT',expressions=A.expressions);return B
		return A
	def get_priority(A):return 10
class HandleArrayConstruct(QueryProcessor):
	def initialize_db_resources(C,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_C)}
            (VARIADIC _values {PG_VARIANT_TYPE}[]) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayConstruct
                return HandleArrayConstruct.array_construct(*_values)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(_C)} () RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayConstruct
                return HandleArrayConstruct.array_construct()
            $$
        """;B=State.server;B.run_query(A,database=database)
	@classmethod
	def array_construct(C,*A):A=[unwrap_variant_type(A)for A in A];B=to_variant(A);return B
class HandleArrayCompact(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_compact")}
            (_array {PG_VARIANT_TYPE}) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayCompact
                return HandleArrayCompact.array_compact(_array)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_compact(C,_array):
		A=_array
		if A is _A:A='[]'
		if isinstance(A,VARIANT):A=unwrap_variant_type(A,expected_type=list)
		B=[A for A in A if A is not _A];B=to_variant(B);return B
class HandleArrayConstructCompact(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_D)}
            (VARIADIC _values {PG_VARIANT_TYPE}[]) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayConstructCompact
                return HandleArrayConstructCompact.array_construct_compact(*_values)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_construct_compact(B,*A):return HandleArrayCompact.array_compact(HandleArrayConstruct.array_construct(*A))
class ConvertArrayContainsOperators(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_E)}
            (_value {PG_VARIANT_TYPE}, _array {PG_VARIANT_TYPE}) RETURNS BOOLEAN
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import ConvertArrayContainsOperators
                return ConvertArrayContainsOperators.array_contains(_value, _array)
            $$
        """;State.server.run_query(A,database=database)
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.ArrayContains):B=exp.Anonymous(this='ARRAY_CONTAINS',expressions=[A.expression,A.this]);return B
		return A
	@classmethod
	def array_contains(D,_value,_array):
		B=_array;A=_value;A=unwrap_variant_type(A);B=unwrap_variant_type(B,expected_type=list)
		for C in B:
			if A==C:return _B
		return False
	def get_priority(A):return 10
class ConvertArrayFunctionArgTypes(QueryProcessor):
	def transform_query(E,expression,**B):
		A=expression;C=_F,_G,_C,_D,_E,_H,_I
		for D in C:A=A.transform(convert_function_args_to_variant,D,**B)
		return A
	def get_priority(C):from snowflake_local.engine.processors.types import ReplaceVariantCastWithToVariant as A;B=[ConvertArrayContainsOperators().get_priority(),ConvertArrayConstructor().get_priority(),A().get_priority()];return min(B)-1
class HandleIsArray(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
        CREATE OR REPLACE FUNCTION {get_canonical_name(_J)} (_input TEXT) RETURNS BOOLEAN
        LANGUAGE plpython3u IMMUTABLE
        AS $$
            from snowflake_local.engine.processors.arrays import HandleIsArray
            return HandleIsArray.is_array(_input)
        $$;
        """;State.server.run_query(A,database=database)
	def transform_query(C,expression,**B):A=expression;A=A.transform(convert_function_args_to_variant,_J,**B);return A
	@classmethod
	def is_array(B,_input):A=_input;A=unwrap_variant_type(A);return isinstance(A,list)
class HandleArrayConcat(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_G)}
            (_array1 {PG_VARIANT_TYPE}, _array2 {PG_VARIANT_TYPE}) RETURNS TEXT
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayConcat
                return HandleArrayConcat.array_concat(_array1, _array2)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_concat(D,_array1,_array2):
		B=_array2;A=_array1;A=unwrap_variant_type(A,expected_type=list);B=unwrap_variant_type(B,expected_type=list)
		if not isinstance(A,list):raise Exception(f"Expected array as first parameter, got: {A}")
		if not isinstance(B,list):raise Exception(f"Expected array as second parameter, got: {B}")
		C=A+B;return to_variant(C)
class EncodeMultiDimensionalArraysAsVariant(QueryProcessor):
	def transform_query(E,expression,**F):
		A=expression
		if not isinstance(A,exp.Array):return A
		D=[A for A in A.expressions if isinstance(A,exp.Array)]
		if not D:return A
		def C(obj):
			B=obj;A=str(B)
			if isinstance(B,exp.Array):
				A=[]
				for D in B.expressions:A.append(C(D))
			if isinstance(B,exp.Literal):
				A=B.this
				if B.is_number:
					A=float(B.this)
					if int(A)==A:A=int(A)
			if isinstance(B,exp.Boolean):A=B.this
			if isinstance(B,exp.Null):A=_A
			return A
		B=C(A);B=to_variant(B);return exp.Literal(this=B,is_string=_B)
class HandleArrayExcept(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_except")}
            (_array {PG_VARIANT_TYPE}, _array_to_exclude {PG_VARIANT_TYPE}) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayExcept
                return HandleArrayExcept.array_except(_array, _array_to_exclude)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_except(E,_array,_array_to_exclude):
		B=_array;A=_array_to_exclude
		if B is _A or A is _A:return to_variant(_A)
		C=unwrap_variant_type(B,expected_type=list);A=unwrap_variant_type(A,expected_type=list)
		for D in A:
			try:C.remove(D)
			except ValueError:pass
		return to_variant(C)
class HandleArrayAppend(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_F)}
            (_array {PG_VARIANT_TYPE}, _entry TEXT) RETURNS TEXT
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayAppend
                return HandleArrayAppend.array_append(_array, _entry)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_append(C,_array,_item):
		B=_item;A=_array
		if A is _A:A='[]'
		A=unwrap_variant_type(A,expected_type=list)
		if not isinstance(A,list):raise Exception(f"Expected array as first parameter, got: {A}")
		B=unwrap_variant_type(B);A.append(B);return to_variant(A)
class HandleArrayFlatten(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_flatten")} (_array {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayFlatten
                return HandleArrayFlatten.array_flatten(_array)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_flatten(D,_array):
		B=_array;B=unwrap_variant_type(B,expected_type=list);C=[]
		for A in B:
			if A is _A:return to_variant(_A)
			A=unwrap_potential_variant_type(A)
			if not isinstance(A,list):raise Exception("Not an array: 'Input argument to ARRAY_FLATTEN is not an array of arrays'")
			C.extend(A)
		return to_variant(C)
class HandleArrayGenerateRange(QueryProcessor):
	def initialize_db_resources(D,database):A='array_generate_range';B=State.server;C=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)}
            (_start INT, _stop INT) RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayGenerateRange
                return HandleArrayGenerateRange.generate_range(_start, _stop)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)}
            (_start INT, _stop INT, _step INT) RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayGenerateRange
                return HandleArrayGenerateRange.generate_range(_start, _stop, _step)
            $$
        """;B.run_query(C,database=database)
	@classmethod
	def generate_range(B,_start,_stop,_step=1):A=list(range(_start,_stop,_step));return to_variant(A)
class HandleArrayInsert(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_K)}
            (_array {PG_VARIANT_TYPE}, _pos INT, _item {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayInsert
                return HandleArrayInsert.array_insert(_array, _pos, _item)
            $$
        """;A.run_query(B,database=database)
	def transform_query(B,expression,query):
		A=expression
		if isinstance(A,exp.Anonymous)and str(A.this).lower()==_K:
			if len(A.expressions)>=3:A.expressions[2]=exp.Anonymous(this='to_variant',expressions=[A.expressions[2]])
		return A
	@classmethod
	def array_insert(D,_array,_pos,_item):
		C=_array;B=_item
		if C is _A:return to_variant(_A)
		A=unwrap_variant_type(C,expected_type=list);B=unwrap_variant_type(B)
		while len(A)<_pos:A.append(_A)
		A.insert(_pos,B);return to_variant(A)
class HandleArrayDistinct(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_distinct")}
            (_array {PG_VARIANT_TYPE}) RETURNS {PG_VARIANT_TYPE}
            LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayDistinct
                return HandleArrayDistinct.array_distinct(_array)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_distinct(D,_array):
		B=_array
		if B is _A:return to_variant(_A)
		B=unwrap_variant_type(B,expected_type=list);A=[]
		for C in B:
			if C not in A:A.append(C)
		A=to_variant(A);return A
class HandleArrayIntersection(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_intersection")}
            (_array1 {PG_VARIANT_TYPE}, _array2 {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayIntersection
                return HandleArrayIntersection.array_intersection(_array1, _array2)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_intersection(E,_array1,_array2):
		B=_array2;A=_array1
		if A is _A or B is _A:return to_variant(_A)
		A=unwrap_variant_type(A,expected_type=list);B=unwrap_variant_type(B,expected_type=list);C=[]
		for D in A:
			try:B.remove(D);C.append(D)
			except ValueError:pass
		return to_variant(C)
class HandleArrayMax(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_max")} (_array {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayMax
                return HandleArrayMax.array_max(_array)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_max(C,_array):
		A=_array
		if A is _A:return to_variant(_A)
		A=unwrap_variant_type(A,expected_type=list);A=[unwrap_potential_variant_type(A)for A in A];A=[A for A in A if A is not _A]
		if not A:return to_variant(_A)
		try:B=max(A)
		except TypeError:A=[str(A)for A in A];B=max(A)
		return to_variant(str(B))
class HandleArrayMin(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_min")} (_array {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayMin
                return HandleArrayMin.array_min(_array)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_min(C,_array):
		A=_array
		if A is _A:return to_variant(_A)
		A=unwrap_variant_type(A,expected_type=list);A=[unwrap_potential_variant_type(A)for A in A];A=[A for A in A if A is not _A]
		if not A:return to_variant(_A)
		try:B=min(A)
		except TypeError:A=[str(A)for A in A];B=min(A)
		return to_variant(str(B))
class HandleArrayPosition(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_position")}
            (_item {PG_VARIANT_TYPE}, _array {PG_VARIANT_TYPE})
            RETURNS INTEGER LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayPosition
                return HandleArrayPosition.array_position(_item, _array)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_position(C,_item,_array):
		B=_item;A=_array
		if A is _A:return
		B=unwrap_potential_variant_type(B);A=unwrap_variant_type(A,expected_type=list)
		try:return A.index(B)
		except Exception:return
class HandleArrayPrepend(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_H)}
            (_array {PG_VARIANT_TYPE}, _item {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayPrepend
                return HandleArrayPrepend.array_prepend(_array, _item)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_prepend(C,_array,_item):
		B=_item;A=_array
		if A is _A:return to_variant(_A)
		B=unwrap_variant_type(B);A=unwrap_variant_type(A,expected_type=list);A.insert(0,B);return to_variant(A)
class HandleArrayRemove(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(_I)}
            (_array {PG_VARIANT_TYPE}, _item {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayRemove
                return HandleArrayRemove.array_remove(_array, _item)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_remove(D,_array,_item):
		B=_item;A=_array
		if A is _A:return to_variant(_A)
		B=unwrap_variant_type(B);A=unwrap_variant_type(A,expected_type=list);C=[A for A in A if A!=B];return to_variant(C)
class HandleArrayRemoveAt(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_remove_at")}
            (_array {PG_VARIANT_TYPE}, _position INT)
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArrayRemoveAt
                return HandleArrayRemoveAt.array_remove_at(_array, _position)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_remove_at(D,_array,_position):
		C=_position;B=_array
		if B is _A:return to_variant(_A)
		A=unwrap_variant_type(B,expected_type=list)
		if C<len(A):A.pop(C)
		return to_variant(A)
class HandleArraySize(QueryProcessor):
	def initialize_db_resources(C,database):A=State.server;B=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_size")}
            (_array {PG_VARIANT_TYPE}) RETURNS INT LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraySize
                return HandleArraySize.array_size(_array)
            $$
        """;A.run_query(B,database=database)
	@classmethod
	def array_size(C,_array):
		A=_array
		if A is _A:return
		B=unwrap_variant_type(A,expected_type=list);return len(B)
class HandleArraySlice(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("array_slice")}
            (_array {PG_VARIANT_TYPE}, _from INT, _to INT)
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraySlice
                return HandleArraySlice.array_slice(_array, _from, _to)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def array_slice(D,_array,_from,_to):
		C=_from;B=_array
		if B is _A or C is _A or _to is _A:return to_variant(_A)
		A=unwrap_variant_type(B,expected_type=list);A=A[C:_to];return to_variant(A)
class HandleArraySort(QueryProcessor):
	def initialize_db_resources(D,database):A='array_sort';B=State.server;C=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)} (_array {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraySort
                return HandleArraySort.array_sort(_array)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)} (_array {PG_VARIANT_TYPE}, _ascending BOOL)
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraySort
                return HandleArraySort.array_sort(_array, _ascending)
            $$;
            CREATE OR REPLACE FUNCTION {get_canonical_name(A)}
            (_array {PG_VARIANT_TYPE}, _ascending BOOL, _nulls_first BOOL)
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraySort
                return HandleArraySort.array_sort(_array, _ascending, _nulls_first)
            $$
        """;B.run_query(C,database=database)
	@classmethod
	def array_sort(H,_array,_ascending=_B,_nulls_first=_A):
		D=_ascending;C=_array;B=_nulls_first
		if C is _A:return to_variant(_A)
		if B is _A:B=not D
		A=unwrap_variant_type(C,expected_type=list);A=[_A if A=='null'else A for A in A];E=[A for A in A if A is _A];F=[A for A in A if A is not _A]
		def G(item1,item2):
			B=item1;A=item2
			if is_number(B):
				if is_number(A):return-1 if float(B)<float(A)else 1
				return 1
			if is_number(A):return-1
			return-1 if str(B)<str(A)else 1
		A=sorted(F,key=cmp_to_key(G),reverse=not D)
		if B:A=E+A
		else:A=A+E
		return to_variant(A)
class HandleArraysOverlap(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("arrays_overlap")}
            (_array1 {PG_VARIANT_TYPE}, _array2 {PG_VARIANT_TYPE})
            RETURNS BOOLEAN LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraysOverlap
                return HandleArraysOverlap.arrays_overlap(_array1, _array2)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def arrays_overlap(D,_array1,_array2):
		B=_array2;A=_array1;A=unwrap_variant_type(A,expected_type=list);B=unwrap_variant_type(B,expected_type=list)
		for C in A:
			if C in B:return _B
		return False
class HandleArraysToObject(QueryProcessor):
	def initialize_db_resources(B,database):A=f"""
            CREATE OR REPLACE FUNCTION {get_canonical_name("arrays_to_object")}
            (_keys_array {PG_VARIANT_TYPE}, _values_array {PG_VARIANT_TYPE})
            RETURNS {PG_VARIANT_TYPE} LANGUAGE plpython3u IMMUTABLE AS $$
                from snowflake_local.engine.processors.arrays import HandleArraysToObject
                return HandleArraysToObject.arrays_to_object(_keys_array, _values_array)
            $$
        """;State.server.run_query(A,database=database)
	@classmethod
	def arrays_to_object(F,_keys_array,_values_array):
		B=_values_array;A=_keys_array;A=unwrap_variant_type(A,expected_type=list);B=unwrap_variant_type(B,expected_type=list)
		if len(A)!=len(B):raise Exception('Key array and value array had unequal lengths in ARRAYS_TO_OBJECT')
		C={}
		for(E,D)in enumerate(A):
			if D is not _A:C[D]=B[E]
		return to_variant(C)