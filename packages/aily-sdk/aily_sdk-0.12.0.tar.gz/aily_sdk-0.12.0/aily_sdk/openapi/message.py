import json

from aily_sdk.openapi import OpenAPIClient


class MessageResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.session_id = None
        if 'data' in result:
            self.session_id = result['data']['session_id']


class MessageClient:
    def __init__(self, client, session):
        self.client = client
        self.session = session

