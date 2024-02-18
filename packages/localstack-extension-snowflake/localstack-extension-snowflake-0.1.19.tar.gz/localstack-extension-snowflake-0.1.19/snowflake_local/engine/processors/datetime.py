_A='TIMESTAMP'
import calendar,datetime,logging
from dateutil.relativedelta import relativedelta
from localstack.utils.time import timestamp
from sqlglot import exp
from snowflake_local.engine.postgres.db_state import State
from snowflake_local.engine.query_processors import QueryProcessor
from snowflake_local.engine.transform_utils import get_canonical_name
LOG=logging.getLogger(__name__)
class ConvertTimestampTypes(QueryProcessor):
	def transform_query(D,expression,**E):
		B='kind';A=expression
		if isinstance(A,exp.ColumnDef):
			C=str(A.args.get(B,'')).upper()
			if C==_A:A.args[B]=exp.Identifier(this='TIMESTAMP WITHOUT TIME ZONE',quoted=False)
		return A
class CastParamsForToDate(QueryProcessor):
	def transform_query(C,expression,**D):
		A=expression
		if isinstance(A,exp.Func)and str(A.this).lower()=='to_date':
			A=A.copy();B=exp.Cast();B.args['this']=A.expressions[0];B.args['to']=exp.DataType.build('TEXT');A.expressions[0]=B
			if len(A.expressions)<=1:LOG.info('Auto-detection of date format in TO_DATE(..) not yet supported');A.expressions.append(exp.Literal(this='YYYY/MM/DD',is_string=True))
		return A
class ReplaceCurrentTime(QueryProcessor):
	def transform_query(D,expression,**E):
		A=expression
		if isinstance(A,(exp.CurrentTime,exp.CurrentTimestamp)):
			B=exp.Literal();C=timestamp()
			if isinstance(A,exp.CurrentTime):C=str(datetime.datetime.utcnow().time())
			B.args['this']=C;B.args['is_string']=True;return B
		return A
class HandleAddMonths(QueryProcessor):
	def initialize_db_resources(D,database):
		B=State.server
		for A in['DATE',_A]:C=f"""
                CREATE OR REPLACE FUNCTION {get_canonical_name("add_months")}
                (_datetime {A}, _months INTEGER) RETURNS {A}
                LANGUAGE plpython3u IMMUTABLE AS $$
                    from snowflake_local.engine.processors.datetime import HandleAddMonths
                    return HandleAddMonths.add_months(_datetime, _months)
                $$
            """;B.run_query(C,database=database)
	@classmethod
	def add_months(G,_datetime,num_months):
		D=_datetime;C='%Y-%m-%d'
		if':'in D:C=C+' %H:%M:%S'
		A=datetime.datetime.strptime(D,C);B=A+relativedelta(months=num_months);F=calendar.monthrange(A.year,A.month)[1];E=calendar.monthrange(B.year,B.month)[1]
		if E<A.day or F==A.day:B=B.replace(day=E)
		return B.strftime(C)