import os

import requests

from ...utilities import get_json_or_error


def cloud_upload(files, server, bucket, subfolder="test", cloud_provider='google', org_config_id=None, api_key=None):
    urls = {}
    for filepath in files:
        url = upload_file(bucket, filepath, server, subfolder, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)
        urls[filepath] = url
    return urls


def upload_file(bucket, filepath, server, subfolder, cloud_provider='google', org_config_id=None, api_key=None):
    url = get_upload_url(bucket, filepath, server, subfolder, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)
    upload_file_to_url(filepath, url, cloud_provider=cloud_provider, api_key=api_key)
    return url


def upload_file_to_url(filepath, url, cloud_provider='google', api_key=None):
    if cloud_provider == 'google':
        content_length = os.path.getsize(filepath)
        payload = open(filepath, "rb")
        headers = {
            'Content-Length': f'{content_length}',
            'Content-Type': 'text/plain'
        }
        if api_key:
            headers['app_key'] = api_key
        response = requests.request("PUT", url, headers=headers, data=payload)
        print(response.text)
    else:
        with open(filepath, 'rb') as file_to_upload:
            files = {'file': (filepath, file_to_upload)}
            upload_response = requests.post(url['url'], data=url['fields'], files=files)
            print(upload_response.text)


def get_upload_url(bucket, filepath, server, subfolder, cloud_provider='google', org_config_id=None, api_key=None):
    remote_url = get_remote_url(bucket, filepath, server, subfolder, cloud_provider=cloud_provider, org_config_id=org_config_id)
    headers = {}
    if api_key:
        headers['app_key'] = api_key

    url = get_json_or_error(remote_url, headers=headers).get('url')
    return url


def get_remote_url(bucket, filepath, server, subfolder, cloud_provider='google', org_config_id=None, api_key=None):
    key = f"{subfolder}/{os.path.basename(filepath)}"
    remote_url = f'http://{server}/api/resumable_upload?bucket={bucket}&key={key}&cloud_provider={cloud_provider}'
    if api_key:
        remote_url += f"&app_key={api_key}"
    if org_config_id:
        remote_url += f"&org_config_id={org_config_id}"
    return remote_url
