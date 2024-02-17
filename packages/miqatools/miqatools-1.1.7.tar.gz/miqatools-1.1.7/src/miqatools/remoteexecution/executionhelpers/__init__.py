import requests

from ...utilities import get_json_or_error


def complete_exec(exec_id, facet_server=None, quiet=True, api_key=None, failed=False):
    if not quiet:
        print(f"Completing execution {exec_id}")
    remote_url = f'https://{facet_server}/api/execution/{exec_id}/mark_{"complete" if not failed else "failed"}'
    headers = {}
    if api_key:
        headers['app_key'] = api_key
    info = get_json_or_error(remote_url, headers=headers)
    if not quiet:
        print(info.get('message'))
    return info


def get_exec_info(exec_id, facet_server=None, api_key=None):
    remote_url = f'https://{facet_server}/api/execution/{exec_id}'
    headers = {}
    if api_key:
        headers['app_key'] = api_key
    info = get_json_or_error(remote_url, headers=headers)
    return info


def get_exec_url(exec_id, facet_server=None):
    return f'https://{facet_server}/execution/{exec_id}'
