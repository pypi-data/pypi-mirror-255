import logging

import requests


class OpenAPIClient:
    def __init__(self, user_access_token):
        self.user_access_token = user_access_token

    def get(self, url, headers=None, data=None, query=None):
        _headers = {
            'Authorization': f'Bearer {self.user_access_token}',
            'Content-Type': 'application/json',
        }
        if headers:
            _headers.update(headers)
        resp = requests.get(url, headers=_headers, json=data, params=query)

        print(f'logid= {resp.headers["X-Tt-Logid"]} content= {resp.content}')
        return resp.json()

    def post(self, url, headers=None, data=None):
        _headers = {
            'Authorization': f'Bearer {self.user_access_token}',
            'Content-Type': 'application/json',
        }
        if headers:
            _headers.update(headers)
        resp = requests.post(url, headers=_headers, json=data)
        print(f'logid= {resp.headers["X-Tt-Logid"]} content= {resp.content}')
        return resp.json()
