from ..executionhelpers import get_exec_info
from ..uploadhelpers import upload_files_or_folder, upload_files_or_folder_async


def upload_files_or_folder_for_exec(exec_id, server, args_folder=None, args_files=None, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None, quiet=True, per_request_timeout=None):
    exec_info = get_exec_info(exec_id, server)
    bucket = exec_info.get('bucket')
    key = exec_info.get('key')
    cloud_provider = exec_info.get('cloud_provider', 'aws')
    org_config_id = exec_info.get('org_config_id')
    upload_files_or_folder(args_folder, server, bucket, key, cloud_provider, org_config_id, args_files,
                           filepattern=filepattern_end, filepattern_start=filepattern_start,
                           exclude_filepattern_end=exclude_filepattern_end,
                           max_filesize=max_filesize, api_key=api_key,
                           max_connections=max_connections, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout)


async def upload_files_or_folder_for_exec_async(exec_id, server, args_folder=None, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None, quiet=True):
    """
      Uploads the test output files from the specified filepath to the corresponding Miqa execution.

      :param exec_id: Execution ID
      :param server: Miqa server e.g. yourco.miqa.io
      :param args_folder: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param filepattern_end: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param filepattern_start: Pattern to match in the file prefix, e.g. 'Analysis/' (Optional)
      :param exclude_filepattern_end: Pattern to exclude in the file suffix, e.g. '.bam' (Optional)
      :param api_key: API key, if required by your Miqa instance (Optional)
      :param int max_connections: Maximum number of connections for parallel upload (Optional)
      :param int max_filesize: Maximum filesize to upload, i.e. if avoiding very large files (Optional)
      :param bool skip_completed: Whether to skip uploading files if there is already an execution with status Done, Failed, or Cancelled (Optional, default True)
      :param filepatterns: List of regex strings representing file patterns to match, e.g. ['*.csv','*.vcf'] (Optional)
      :param bool quiet: Whether to skip logging. Default True. (Optional)
      """
    exec_info = get_exec_info(exec_id, server)
    bucket = exec_info.get('bucket')
    key = exec_info.get('key')
    cloud_provider = exec_info.get('cloud_provider', 'aws')
    org_config_id = exec_info.get('org_config_id')
    await upload_files_or_folder_async(args_folder, server, bucket, key, cloud_provider, org_config_id,
                                       filepattern=filepattern_end, filepattern_start=filepattern_start,
                                       exclude_filepattern_end=exclude_filepattern_end,
                                       max_filesize=max_filesize, api_key=api_key,
                                       max_connections=max_connections, filepatterns=filepatterns, quiet=quiet)
