import os.path
from localstack.aws.connect import connect_to
from localstack.utils.aws.resources import get_or_create_bucket
from snowflake_local import config
from snowflake_local.config import ASSETS_BUCKET_NAME,ASSETS_KEY_PREFIX
from snowflake_local.files.storage import FileRef,StageType
def get_stage_s3_location(file_ref):
	E='test';A=file_ref;B=A.get_path().lstrip('/');get_or_create_bucket(ASSETS_BUCKET_NAME,s3_client=connect_to().s3);C=f"{ASSETS_BUCKET_NAME}/{ASSETS_KEY_PREFIX}"
	if A.stage.stage_type==StageType.USER:D=f"{C}{B}"
	else:D=f"{C}{os.path.dirname(B)}"
	return{'locationType':'S3','region':'us-east-1','endPoint':config.S3_ENDPOINT,'location':D,'creds':{'AWS_KEY_ID':E,'AWS_SECRET_KEY':E}}