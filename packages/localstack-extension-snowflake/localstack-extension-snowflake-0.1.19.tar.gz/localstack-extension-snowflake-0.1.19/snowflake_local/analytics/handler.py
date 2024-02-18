_A='snowflake.'
import json,logging,traceback
from typing import NamedTuple
from localstack import config
from localstack.aws.api import RequestContext
from localstack.aws.chain import ExceptionHandler,HandlerChain
from localstack.http import Response
from localstack.utils.analytics import EventLogger,log
from localstack.utils.strings import to_str
from rolo import Response as RoloResponse
from snowflake_local import config as sf_config
from snowflake_local import constants
from snowflake_local.server.models import QueryException
from snowflake_local.server.routes import get_request_data
LOG=logging.getLogger(__name__)
class SnowflakeEvent(NamedTuple):method:str;route:str;status_code:int;version:str;user_agent:str;exc_msg:str
EVENT_NAME='extensions_sf_event'
class SnowflakeAnalyticsHandler:
	def __init__(A,event_logger=None):A.handler=event_logger or log
	def __call__(C,chain,context,response):
		A=context
		if _A not in A.request.url:return
		if config.DISABLE_EVENTS:return
		B=getattr(A,'snowflake_exception',None);D=SnowflakeEvent(route=A.request.path,method=A.request.method,status_code=response.status_code,version=constants.VERSION,user_agent=A.request.user_agent.string,exc_msg=B.message if B else'');C.handler.event(EVENT_NAME,D._asdict())
class QueryFailureHandler(ExceptionHandler):
	def __call__(D,chain,exception,context,response):
		B=context;A=exception
		if _A not in B.request.url:return
		if not isinstance(A,QueryException):return
		C=D.build_exception_response(A,B)
		if C:response.update_from(C)
	def build_exception_response(D,exception,context):
		A=exception;B=A.query_data;context.snowflake_exception=A;C=Response.for_json(B.to_dict(),status=200)
		if config.DEBUG:A.message=''.join(traceback.format_exception(type(A),value=A,tb=A.__traceback__))
		return C
class TraceLoggingHandler:
	def __call__(G,chain,context,response):
		E=context;A=response
		if not sf_config.TRACE_LOG:return
		if _A not in E.request.url:return
		D=E.request;B=get_request_data(D)
		if isinstance(B,dict):B=json.dumps(B)
		F=None;C=str(A)
		if isinstance(A,(Response,RoloResponse)):
			F=A.status_code;C=A.data
			try:C=to_str(C)
			except Exception:pass
		LOG.debug('REQ: %s %s %s -- RES: %s %s',D.method,D.path,B,F,C)