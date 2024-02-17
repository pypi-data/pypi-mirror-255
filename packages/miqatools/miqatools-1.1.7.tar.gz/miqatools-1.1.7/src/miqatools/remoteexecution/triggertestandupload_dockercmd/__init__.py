from argparse import ArgumentParser

from ..triggertest_helpers import trigger_miqa_test, get_tcr_info_json


def get_upload_command(miqa_server, run_id, directory_containing_outputs='$(pwd)', api_key=None):
    get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs, api_key=api_key)
    upload_command = get_info_response_json.get("upload_command")
    return upload_command


def trigger_test_and_get_command(miqa_server, trigger_id, version_name, directory_containing_outputs='$(pwd)', api_key=None):
    run_id = trigger_miqa_test(miqa_server, trigger_id, version_name, api_key=api_key)
    upload_command = get_upload_command(miqa_server, run_id, directory_containing_outputs, api_key=api_key)
    return upload_command


# Example usage
# upload_cmd = trigger_test_and_get_command("{your trigger ID}", "{your version}", "{your directory}")
# upload_cmd = trigger_test_and_get_command("c1890d2c", "offline_Aug11_1236", "/Users/gwennberry/Desktop/test-data/demo_vcf_S21")


# Use the above as a starting point if you want to embed in your own scripts, or run as a CLI program as demonstrated below.
# If you'd rather or require to skip the Docker piece altogether,
# ask us about direct upload API via python!
if __name__ == '__main__':
    parser = ArgumentParser(description='A command line tool for interacting with the Miqa API')
    parser.add_argument('--trigger_id', type=str, default=None, help='Trigger ID in Miqa')
    parser.add_argument('--server', type=str, default=None, help='Miqa Server URL')
    parser.add_argument('--version_name', type=str, default=None, help='Version Name to create (e.g. MyPipeline v1.0, or commit ID e.g. abc123de')
    parser.add_argument('--directory', type=str, default='$(pwd)', help='Path to local directory containing files to upload')
    parser.add_argument('--api_key', type=str, default='', help='API Key to access Miqa API')
    args = parser.parse_args()

    if args.trigger_id and args.server and args.version_name:
        upload_cmd = trigger_test_and_get_command(args.server, args.trigger_id, args.version_name, args.directory)
        print(upload_cmd)
