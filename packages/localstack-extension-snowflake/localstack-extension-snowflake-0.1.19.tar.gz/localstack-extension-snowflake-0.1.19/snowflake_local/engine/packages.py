_A='pg-plv8'
import os,shutil
from typing import List
from localstack import config
from localstack.packages import InstallTarget,Package,PackageInstaller
from localstack.packages.core import ArchiveDownloadAndExtractInstaller
from localstack.utils.files import cp_r,file_exists_not_empty
from localstack.utils.http import download
from localstack.utils.platform import get_arch
PG_PLV8_URL='https://localstack-assets.s3.amazonaws.com/postgres-<pg_version>-plv8-<arch>.zip'
POSTGRES_VERSION='15'
class PostgresPlv8Package(Package):
	def __init__(A):super().__init__(_A,POSTGRES_VERSION)
	def get_versions(A):return[POSTGRES_VERSION]
	def _get_installer(A,version):return PostgresPlv8Installer(version)
class PostgresPlv8Installer(ArchiveDownloadAndExtractInstaller):
	def __init__(A,version):super().__init__(_A,version)
	def _get_install_marker_path(A,install_dir):return f"/usr/share/postgresql/{POSTGRES_VERSION}/extension/plv8.control"
	def _get_download_url(B):A=PG_PLV8_URL.replace('<pg_version>',POSTGRES_VERSION);A=A.replace('<arch>',get_arch());return A
	def _post_process(A,target):B=A._get_install_dir(target);cp_r(os.path.join(B,'usr'),'/usr')
	def _install(D,target):
		B=D._get_download_url();C=os.path.basename(B);A=os.path.join(config.dirs.cache,C);E=os.path.join(config.dirs.tmp,C)
		if not file_exists_not_empty(A):download(B,A)
		shutil.copy(A,E);super()._install(target=target)
postgres_plv8_package=PostgresPlv8Package()