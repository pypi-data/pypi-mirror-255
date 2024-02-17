import asyncio
import os
import re
import threading
import time

import aiohttp
import requests
from aiohttp import FormData

from ..baseuploadhelpers import get_remote_url, cloud_upload


async def upload_folder_async(folder, server, bucket, subfolder="folder-up3", filepattern=None, filepattern_start=None, quiet=True, cloud_provider='google', org_config_id=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None, per_request_timeout=None):
    if not quiet:
        print(f"Uploading folder {folder}")
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(folder)) for f in fn if
             not f.endswith(".DS_Store")]
    max_files = len(files)
    sorted_files = sorted({k:os.stat(k).st_size for k in files if (not max_filesize or (os.stat(k).st_size/(1024*1024) < max_filesize))}.items(), key=lambda kv: kv[1])
    filesize_msg = f'(filtered out {(max_files - len(sorted_files))} by size)' if max_filesize else ''
    if not quiet:
        print(f"Processing up to {len(sorted_files)} files from this directory {filesize_msg}...")

    session_timeout = aiohttp.ClientTimeout(total=per_request_timeout)
    if max_connections:
        connector = aiohttp.TCPConnector(limit=max_connections)
        client = aiohttp.ClientSession(connector=connector, timeout=session_timeout)
    else:
        client = aiohttp.ClientSession(timeout=session_timeout)
    async with client as session:
        num_processed = 0
        num_skipped = 0
        file_times_miqa = {}
        file_times_cloud = {}

        for file, filesize in sorted_files:
            if (not filepatterns or check_any_pattern_matches(filepatterns, file)) and (not filepattern or file.endswith(filepattern)) and (not filepattern_start or file.startswith(filepattern_start)) and (not exclude_filepattern_end or not file.endswith(exclude_filepattern_end)):
                if not quiet:
                    print(f"{file}: {round(filesize/ (1024 * 1024),5)}MB")
                subsubfolder = "/".join(file[len(folder)+1:].split("/")[:-1])
                filepath = os.path.join(folder, file)
                if os.path.isdir(filepath):
                    num_skipped+=1
                    if not quiet:
                        print(f"Skipping directory: {num_skipped} total skipped so far")
                    continue
                num_processed += 1

                start_miqaremote = time.perf_counter()
                remote_url = get_remote_url(bucket, filepath, server, subfolder+"/"+subsubfolder, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)
                end_miqaremote = time.perf_counter()
                time_miqaremote = end_miqaremote - start_miqaremote
                file_times_miqa[filepath] = time_miqaremote

                headers = {}
                if api_key:
                    headers['app_key'] = api_key
                async with session.get(remote_url, headers=headers) as response:
                    if not quiet:
                        print(f"Threads: {threading.active_count()}")
                        print("Status:", response.status)
                        print("Content-type:", response.headers['content-type'])

                    if response.status != 200:
                        print(f"ERROR: Unable to post file: response status was {response.status}")
                        json_r = await response.json()
                        if json_r and json_r.get('message'):
                            print(json_r.get('message'))
                        print("------------------------------------")
                        return

                    json_r = await response.json()
                    if not quiet:
                        print(json_r)
                    new_url = json_r.get('url')
                    content_length = os.path.getsize(filepath)
                    payload = open(filepath, "rb")
                    headers = {
                        'Content-Length': f'{content_length}',
                        'Content-Type': 'text/plain'
                    }

                    start_cloudupload = time.perf_counter()
                    if cloud_provider == 'google':
                        async with session.put(new_url, data=payload, headers=headers) as response:
                            if not quiet:
                                print(f"submitted {filepath}")
                                print(response)
                    else:
                        data = FormData()
                        for dk, dv in new_url.get('fields', {}).items():
                            data.add_field(dk, dv)
                        data.add_field('file', open(filepath, 'rb'))
                        async with session.post(new_url.get('url'), data=data) as response:
                            if not quiet:
                                print(f"submitted {filepath}")
                    end_cloudupload = time.perf_counter()
                    time_cloudupload = end_cloudupload - start_cloudupload
                    file_times_cloud[filepath] = time_cloudupload
                    print(f"Time to upload {filepath}: {round(time_cloudupload + time_miqaremote,4)}s")
        if not quiet:
            total_cloud_time = sum(file_times_cloud.values())
            total_miqa_time = sum(file_times_miqa.values())
            print(f"Done uploading for {num_processed} file(s). Total time: {round(total_cloud_time+total_miqa_time, 4)}s. {round(total_miqa_time, 4)}s on Miqa requests and {round(total_cloud_time, 4)}s on cloud uploads (Per-File Average {round(total_miqa_time/len(file_times_miqa), 4)}s Miqa / {round(total_cloud_time/len(file_times_cloud), 4)}s Cloud ; Max {round(max(file_times_miqa.values()), 4)}s Miqa / {round(max(file_times_cloud.values()), 4)}s).")


def check_any_pattern_matches(filepatterns, file):
    for filepattern in filepatterns:
        if check_pattern_match(filepattern, file):
            return True
    return False


def upload_folder_sync(folder, server, bucket, subfolder="folder-up3", filepattern=None, filepattern_start=None, quiet=True, cloud_provider='google', org_config_id=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None):
    if not quiet:
        print("Processing folder synchronously...")
        print(f"Uploading folder {folder}")
    files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(folder)) for f in fn if
             not f.endswith(".DS_Store")]
    max_files = len(files)
    sorted_files = sorted({k:os.stat(k).st_size for k in files if (not max_filesize or (os.stat(k).st_size/(1024*1024) < max_filesize))}.items(), key=lambda kv: kv[1])
    filesize_msg = f'(filtered out {(max_files - len(sorted_files))} by size)' if max_filesize else ''
    if not quiet:
        print(f"Processing up to {len(sorted_files)} files from this directory {filesize_msg}...")

    num_processed = 0
    num_skipped = 0
    for file, filesize in sorted_files:
        if (not filepatterns or check_any_pattern_matches(filepatterns, file)) and (not filepattern or file.endswith(filepattern)) and (not filepattern_start or file.startswith(filepattern_start)) and (not exclude_filepattern_end or not file.endswith(exclude_filepattern_end)):
            if not quiet:
                print(f"{file}: {round(filesize/ (1024 * 1024),3)}MB")
            subsubfolder = "/".join(file[len(folder)+1:].split("/")[:-1])
            filepath = os.path.join(folder, file)
            if os.path.isdir(filepath):
                num_skipped+=1
                if not quiet:
                    print(f"Skipping directory: {num_skipped} total skipped so far")
                continue
            num_processed += 1
            remote_url = get_remote_url(bucket, filepath, server, subfolder+"/"+subsubfolder, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)
            headers = {}
            if api_key:
                headers['app_key'] = api_key
            response = requests.get(remote_url, headers=headers)
            if not quiet:
                print("Status:", response.status_code)
                print("Content-type:", response.headers['content-type'])

            if response.status_code != 200:
                print(f"ERROR: Unable to post file: response status was {response.status_code}")
                json_r = response.json()
                if json_r and json_r.get('message'):
                    print(json_r.get('message'))
                print("------------------------------------")
                return

            json_r = response.json()
            if not quiet:
                print(json_r)
            new_url = json_r.get('url')
            content_length = os.path.getsize(filepath)
            payload = open(filepath, "rb")
            headers = {
                'Content-Length': f'{content_length}',
                'Content-Type': 'text/plain'
            }

            if cloud_provider == 'google':
                response = requests.put(new_url, data=payload, headers=headers)
                if not quiet:
                    print("submitted")
            else:
                # data = FormData()
                # for dk, dv in new_url.get('fields', {}).items():
                #     data.add_field(dk, dv)
                # data.add_field('file', open(filepath, 'rb'))
                response = requests.post(new_url.get('url'), data=new_url.get('fields', {}), files={'file': open(filepath, 'rb')})
                if not quiet:
                    print("submitted")


def upload_files_or_folder(args_folder, server, bucket, key, cloud_provider, org_config_id, args_files=None,
                           filepattern=None, filepattern_start=None, exclude_filepattern_end=None,
                           max_filesize=None, api_key=None, max_connections=None, filepatterns=None, quiet=True, per_request_timeout=None):
    global loop
    if args_folder:
        if max_connections and max_connections <= 1:
            upload_folder_sync(args_folder, server, bucket, subfolder=key, cloud_provider=cloud_provider,
                                org_config_id=org_config_id, filepattern=filepattern, filepattern_start=filepattern_start, exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key, max_connections=max_connections, filepatterns=filepatterns, quiet=quiet)
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                upload_folder_async(args_folder, server, bucket, subfolder=key, cloud_provider=cloud_provider,
                                    org_config_id=org_config_id, filepattern=filepattern, filepattern_start=filepattern_start, exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key, max_connections=max_connections, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout))
    elif args_files:
        cloud_upload(args_files, server, bucket, key, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)


async def upload_files_or_folder_async(args_folder, server, bucket, key, cloud_provider, org_config_id,
                                       filepattern=None, filepattern_start=None, exclude_filepattern_end=None,
                                       max_filesize=None, api_key=None, max_connections=None, filepatterns=None, quiet=True, per_request_timeout=None):
    await upload_folder_async(args_folder, server, bucket, subfolder=key, cloud_provider=cloud_provider,
                        org_config_id=org_config_id, filepattern=filepattern, filepattern_start=filepattern_start,
                        exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key,
                        max_connections=max_connections, filepatterns=filepatterns, quiet=quiet, per_request_timeout=per_request_timeout)
    # global loop
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(
    #     upload_folder_async(args_folder, server, bucket, subfolder=key, cloud_provider=cloud_provider,
    #                         org_config_id=org_config_id, filepattern=filepattern, filepattern_start=filepattern_start,
    #                         exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key,
    #                         max_connections=max_connections, filepatterns=filepatterns))
    # if args_folder:
    #     if max_connections and max_connections <= 1:
    #         upload_folder_sync(args_folder, server, bucket, subfolder=key, cloud_provider=cloud_provider,
    #                             org_config_id=org_config_id, filepattern=filepattern, filepattern_start=filepattern_start, exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key, max_connections=max_connections, filepatterns=filepatterns)
    #     else:
    # elif args_files:
    #     cloud_upload(args_files, server, bucket, key, cloud_provider=cloud_provider, org_config_id=org_config_id, api_key=api_key)


def check_pattern_match(pattern, path, default=True):
    if pattern is None:
        return default
    match = re.search(pattern, path)
    if match:
        return True
    else:
        return False
