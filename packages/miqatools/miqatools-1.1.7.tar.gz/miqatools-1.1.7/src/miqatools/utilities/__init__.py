import requests


def get_json_or_error(url, headers):
    response = requests.get(url, headers=headers)

    if response and response.ok:
        return response.json()
    else:
        print(response.text)
        raise Exception(f"Error calling endpoint {url}: {response.status_code} {response.text if not 'DOCTYPE html' in response.text else '(See message above)'}")