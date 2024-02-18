from localstack.aws.chain import CompositeExceptionHandler,CompositeResponseHandler
from localstack.extensions.api import Extension
from localstack.extensions.api.http import RouteHandler,Router
class SnowflakeExtension(Extension):
	name='snowflake'
	def update_gateway_routes(B,router):from snowflake_local.server.routes import RequestHandler as A;router.add(A())
	def update_response_handlers(D,handlers):A=handlers;from snowflake_local.analytics.handler import SnowflakeAnalyticsHandler as B,TraceLoggingHandler as C;A.append(B());A.append(C())
	def update_exception_handlers(B,handlers):from snowflake_local.analytics.handler import QueryFailureHandler as A;handlers.append(A())