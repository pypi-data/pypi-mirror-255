import logging,os
from localstack import config
from localstack.config import is_env_not_false
DB_ENGINE='postgres'
ASSETS_BUCKET_NAME='snowflake-assets'
ASSETS_KEY_PREFIX='uploads/'
logger=logging.getLogger('snowflake_local')
logger.setLevel(logging.INFO)
if config.DEBUG:logger.setLevel(logging.DEBUG)
logging.getLogger('sqlglot').setLevel(logging.ERROR)
SF_LOG=os.getenv('SF_LOG','').strip()
TRACE_LOG=SF_LOG.lower()=='trace'
S3_ENDPOINT=os.getenv('SF_S3_ENDPOINT','').strip()or's3.localhost.localstack.cloud:4566'
CONVERT_NAME_CASING=is_env_not_false('CONVERT_NAME_CASING')
RETURN_SELECT_AS_ARROW=is_env_not_false('RETURN_SELECT_AS_ARROW')