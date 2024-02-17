import json
import pprint
from dataclasses import dataclass
from typing import Optional

from aily_sdk.openapi import OpenAPIClient


@dataclass
class MessageResponse:
    code: int
    msg: int
    intent_id: Optional[str] = None
    message_id: Optional[str] = None


@dataclass
class OperationResponse:
    code: int
    msg: int
    last_operation_id: str
    intent_finished: bool
    operations: list

    def get_last_system_message(self):
        pprint.pprint(self.operations)
        for op in self.operations:
            if op['message']['sender']['sender_type'] not in ['SYSTEM', 'SKILL']:
                continue
            return op['message']


class Session:
    def __init__(self, client: OpenAPIClient, app_id: str):
        self.client = client
        self.app_id = app_id
        self.base_url = 'https://open.feishu.cn/open-apis/aily/v1/apps/'
        self.session_id = None

    def create(self, enable_debug: bool = False, channel_context: Optional[dict] = None):
        url = f'{self.base_url}{self.app_id}/sessions'
        channel_context = channel_context or {}

        data = {
            'enable_debug': enable_debug,
            'channel_context': json.dumps(channel_context)  # 确认 channel_context 需要的格式
        }

        try:
            response = self.client.post(url, data=data)
            self.session_id = response.get('data', {}).get('session_id')
            return self
        except Exception as e:
            print(f'创建会话时发生错误: {e}')

    @property
    def random_str(self):
        import random
        import string

        # 目标字符串
        target_string = "S9GiePojDRLuGFv-G8BZQ"
        # 计算目标字符串的长度
        length_of_target = len(target_string)

        # 生成一个相同长度的随机字符串
        # 包括大写字母、小写字母和数字
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length_of_target))

        return random_string

    def send_message(self, content, skill_id=None, channel_context: Optional[dict] = None):
        url = f'{self.base_url}{self.app_id}/sessions/{self.session_id}/messages'

        data = {
            "idempotent_id": self.random_str,
            "message": {
                'content': json.dumps(content)
            }
        }
        if skill_id:
            data['skill_id'] = skill_id
        if channel_context:
            data['channel_context'] = skill_id

        # 调用 client 的 post 方法发送请求
        response = self.client.post(url, data=data)
        return MessageResponse(
            code=response['code'], msg=response['msg'],
            intent_id=response.get('data', {}).get('intent_id'),
            message_id=response.get('data', {}).get('message_id')
        )

    def get_message(self, message_id):
        url = f'{self.base_url}{self.app_id}/sessions/{self.session_id}/messages/{message_id}'

        # 调用 client 的 post 方法发送请求
        return self.client.get(url)

    def poll_operation(self, last_operation_id=None):
        url = f'{self.base_url}{self.app_id}/sessions/{self.session_id}/poll'
        data = {}
        if last_operation_id:
            data['last_operation_id'] = last_operation_id
        # 调用 client 的 post 方法发送请求
        response = self.client.post(url, data=data)

        return OperationResponse(
            code=response['code'],
            msg=response['msg'],
            intent_finished=response.get('data', {}).get('intent_finished'),
            last_operation_id=response.get('data', {}).get('last_operation_id'),
            operations=response.get('data', {}).get('operations')
        )

    def get_result(self):
        pass
