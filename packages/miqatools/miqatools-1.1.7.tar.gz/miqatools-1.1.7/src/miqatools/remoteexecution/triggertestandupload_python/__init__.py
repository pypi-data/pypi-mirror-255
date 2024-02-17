from argparse import ArgumentParser

import asyncio

from ..executionhelpers import complete_exec
from ..offlineexecution import upload_files_or_folder_for_exec, upload_files_or_folder_for_exec_async
from ..triggertest_helpers import trigger_miqa_test, get_tcr_info_json


def trigger_test_and_upload_single_results(miqa_server, trigger_id, version_name, directory_containing_outputs, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None, quiet=True, per_request_timeout=None):
    """
      Triggers an offline execution of the specified Miqa trigger ID for the specified version, and then uploads the test output files, from the specified filepath to the corresponding Miqa execution.

      :param str miqa_server: Miqa server e.g. yourco.miqa.io
      :param str trigger_id: Miqa test trigger ID e.g. ABC123
      :param str version_name: Name representing the version that was being tested/generated the outputs being uploaded, e.g. a commit ID ('abc123') or version number ('v1.2.3')
      :param str directory_containing_outputs: Directory filepath containing the test outputs/results to be uploaded
      :param str filepattern_end: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param str filepattern_start: Pattern to match in the file prefix, e.g. 'Analysis/' (Optional)
      :param str exclude_filepattern_end: Pattern to exclude in the file suffix, e.g. '.bam' (Optional)
      :param str api_key: API key, if required by your Miqa instance (Optional)
      :param int max_connections: Maximum number of connections for parallel upload (Optional)
      :param int max_filesize: Maximum filesize to upload, i.e. if avoiding very large files (Optional)
      :param bool skip_completed: Whether to skip uploading files if there is already an execution with status Done (Optional, default True)
      :param list filepatterns: List of regex strings representing file patterns to match, e.g. ['*.csv','*.vcf'] (Optional)
      :param bool quiet: Whether to skip logging. Default True. (Optional)
      :param int per_request_timeout: Timeout for individual requests made during uploading. Default None. (Optional)
      :return: Test chain run ID
      :rtype: int
      """
    run_id = trigger_miqa_test(miqa_server, trigger_id, version_name)
    get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs)
    exec_id = get_info_response_json.get("exec_id")
    upload_files_or_folder_for_exec(exec_id, miqa_server, directory_containing_outputs, None, filepattern_end=filepattern_end,
                                    filepattern_start=filepattern_start, exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key,
                                    max_connections=max_connections, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout)
    complete_exec(exec_id, miqa_server, quiet=quiet)
    return run_id


def trigger_test_and_upload_by_dsid(miqa_server, trigger_id, version_name, ds_lookup, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, skip_completed=True, filepatterns=None, quiet=True, per_request_timeout=None):
    """
      Triggers an offline execution of the specified Miqa trigger ID for the specified version, and then uploads the test output files for each specified dataset, from the specified filepath to the corresponding Miqa execution.

      :param str miqa_server: Miqa server e.g. yourco.miqa.io
      :param str trigger_id: Miqa test trigger ID e.g. ABC123
      :param str version_name: Name representing the version that was being tested/generated the outputs being uploaded, e.g. a commit ID ('abc123') or version number ('v1.2.3')
      :param dict ds_lookup: Dictionary of dataset IDs (int) and their locations (filepath string), e.g. {DS_ID_1:'OUTPUT_LOCATION_FOR_DS_ID_1',DS_ID_2:'OUTPUT_LOCATION_FOR_DS_ID_2'}
      :param str filepattern_end: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param str filepattern_start: Pattern to match in the file prefix, e.g. 'Analysis/' (Optional)
      :param str exclude_filepattern_end: Pattern to exclude in the file suffix, e.g. '.bam' (Optional)
      :param str api_key: API key, if required by your Miqa instance (Optional)
      :param int max_connections: Maximum number of connections for parallel upload (Optional)
      :param int max_filesize: Maximum filesize to upload, i.e. if avoiding very large files (Optional)
      :param bool skip_completed: Whether to skip uploading files if there is already an execution with status Done, Failed, or Cancelled (Optional, default True)
      :param list filepatterns: List of regex strings representing file patterns to match, e.g. ['*.csv','*.vcf'] (Optional)
      :param bool quiet: Whether to skip logging. Default True. (Optional)
      :param int per_request_timeout: Timeout for individual requests made during uploading. Default None. (Optional)
      :return: Test chain run ID
      :rtype: int
      """
    run_id = trigger_miqa_test(miqa_server, trigger_id, version_name, api_key=api_key)
    upload_to_test_by_dsid(run_id, miqa_server, ds_lookup, filepattern_end, filepattern_start, exclude_filepattern_end, api_key,
                           max_connections, max_filesize, skip_completed=skip_completed, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout)
    return run_id


def upload_to_test_by_dsid(run_id, miqa_server, ds_lookup, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, api_key=None,
                           max_connections=None, max_filesize=None, skip_completed=True, filepatterns=None, quiet=True, halt_on_upload_failure=False, halt_on_general_failure=False, per_request_timeout=None):
    """
      Uploads the test output files for each specified dataset, from the specified filepath to the corresponding Miqa execution.

      :param int run_id: Test chain run ID
      :param str miqa_server: Miqa server e.g. yourco.miqa.io
      :param dict ds_lookup: Dictionary of dataset IDs (int) and their locations (filepath string), e.g. {DS_ID_1:'OUTPUT_LOCATION_FOR_DS_ID_1',DS_ID_2:'OUTPUT_LOCATION_FOR_DS_ID_2'}
      :param str filepattern_end: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param str filepattern_start: Pattern to match in the file prefix, e.g. 'Analysis/' (Optional)
      :param str exclude_filepattern_end: Pattern to exclude in the file suffix, e.g. '.bam' (Optional)
      :param str api_key: API key, if required by your Miqa instance (Optional)
      :param int max_connections: Maximum number of connections for parallel upload (Optional)
      :param int max_filesize: Maximum filesize to upload, i.e. if avoiding very large files (Optional)
      :param bool skip_completed: Whether to skip uploading files if there is already an execution with status Done, Failed, or Cancelled (Optional, default True)
      :param filepatterns: List of regex strings representing file patterns to match, e.g. ['*.csv','*.vcf'] (Optional)
      :param bool quiet: Whether to skip logging. Default True. (Optional)
      :param bool halt_on_upload_failure: Whether to halt all processing if there is an error (e.g. timeout) in the upload. Default False. (Optional)
      :param bool halt_on_general_failure: Whether to halt all processing if there is an error (e.g. timeout) other than in the upload. Default False. (Optional)
      :param int per_request_timeout: Timeout for individual requests made during uploading. Default None. (Optional)
       """
    for ds_id, directory_containing_outputs in ds_lookup.items():
        try:
            get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs, ds_id=ds_id)
            exec_id = get_info_response_json.get("exec_id")
            failed = False
            try:
                if skip_completed:
                    if "exec_status" in get_info_response_json:
                        if get_info_response_json.get("exec_status").lower() in ["done", "failed", "cancelled"]:
                            if not quiet:
                                print(f"Skipping upload for {exec_id}: status is already {get_info_response_json.get('exec_status')}")
                            continue
                upload_files_or_folder_for_exec(exec_id, miqa_server, directory_containing_outputs, None,
                                            filepattern_end=filepattern_end,
                                            filepattern_start=filepattern_start,
                                            exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize,
                                            api_key=api_key,
                                            max_connections=max_connections, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout)
            except Exception as e2:
                failed = True
                if not quiet:
                    print(f"Failing {exec_id} for {ds_id} due to unhandled exception (see below). Will mark execution as failed and continue any remaining samples.")
                    print(e2)
                if halt_on_upload_failure:
                    complete_exec(exec_id, miqa_server, quiet=quiet, api_key=api_key, failed=failed)
                    raise
            complete_exec(exec_id, miqa_server, quiet=quiet, api_key=api_key, failed=failed)
        except Exception as e:
            print(f"Failed upload for {ds_id}. See exception below.")
            print(e)
            if halt_on_general_failure:
                raise


def upload_to_test_by_dsid_async(run_id, miqa_server, ds_lookup, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, api_key=None,
                           max_connections=None, max_filesize=None, skip_completed=True, filepatterns=None, quiet=True):
    """
      Uploads the test output files for each specified dataset, from the specified filepath to the corresponding Miqa execution.

      :param int run_id: Test chain run ID
      :param str miqa_server: Miqa server e.g. yourco.miqa.io
      :param dict ds_lookup: Dictionary of dataset IDs (int) and their locations (filepath string), e.g. {DS_ID_1:'OUTPUT_LOCATION_FOR_DS_ID_1',DS_ID_2:'OUTPUT_LOCATION_FOR_DS_ID_2'}
      :param str filepattern_end: Pattern to match in the file suffix, e.g. '.bam' (Optional)
      :param str filepattern_start: Pattern to match in the file prefix, e.g. 'Analysis/' (Optional)
      :param str exclude_filepattern_end: Pattern to exclude in the file suffix, e.g. '.bam' (Optional)
      :param str api_key: API key, if required by your Miqa instance (Optional)
      :param int max_connections: Maximum number of connections for parallel upload (Optional)
      :param int max_filesize: Maximum filesize to upload, i.e. if avoiding very large files (Optional)
      :param bool skip_completed: Whether to skip uploading files if there is already an execution with status Done, Failed, or Cancelled (Optional, default True)
      :param list filepatterns: List of regex strings representing file patterns to match, e.g. ['*.csv','*.vcf'] (Optional)
      :param bool quiet: Whether to skip logging. Default True. (Optional)
      """
    global loop
    loop = asyncio.get_event_loop()
    exec_id_lookup = {}
    for ds_id, directory_containing_outputs in ds_lookup.items():
        get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs, ds_id=ds_id)
        exec_id = get_info_response_json.get("exec_id")
        exec_id_lookup[ds_id] = exec_id
        if skip_completed:
            if "exec_status" in get_info_response_json:
                if get_info_response_json.get("exec_status").lower() in ["done", "failed", "cancelled"]:
                    if not quiet:
                        print(f"Skipping upload for {exec_id}: status is already Done")
                    continue
        loop.run_until_complete(
        upload_files_or_folder_for_exec_async(exec_id, miqa_server, directory_containing_outputs,
                                              filepattern_end=filepattern_end,
                                              filepattern_start=filepattern_start,
                                              exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize,
                                              api_key=api_key,
                                              max_connections=max_connections, filepatterns=filepatterns))

    for ds_id, directory_containing_outputs in ds_lookup.items():
        complete_exec(exec_id_lookup[ds_id], miqa_server, quiet=quiet)


if __name__ == '__main__':
    parser = ArgumentParser(description='A command line tool for interacting with the Miqa API')
    parser.add_argument('--trigger_id', type=str, default=None, help='Trigger ID in Miqa')
    parser.add_argument('--server', type=str, default=None, help='Miqa Server URL')
    parser.add_argument('--version_name', type=str, default=None, help='Version Name to create (e.g. MyPipeline v1.0, or commit ID e.g. abc123de')
    parser.add_argument('--directory', type=str, default=None, help='Path to local directory containing files to upload')
    args = parser.parse_args()

    trigger_test_and_upload_single_results(args.server, args.trigger_id, args.version_name, args.directory)

