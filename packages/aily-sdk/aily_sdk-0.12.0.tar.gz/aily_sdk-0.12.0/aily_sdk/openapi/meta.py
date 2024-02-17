import json

from aily_sdk.openapi import OpenAPIClient


class MetaListResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.has_more = None
        self.total = None
        self.page_token = None
        self.items = []
        if 'data' in result:
            self.has_more = result['data']['has_more']
            self.total = result['data']['total']
            self.page_token = result['data']['page_token']
            self.items = result['data']['items']


class MetaResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.data = None
        if 'data' in result:
            self.data = result['data']


class MetaClient(OpenAPIClient):
    def table_list(self, query_params):
        # 检查必要的参数是否存在
        if 'app_id' not in query_params:
            raise ValueError("Missing required parameter: 'app_id'")

        # 构建请求的 URL
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{query_params["app_id"]}/tables'

        # 移除 app_id，因为它已经被用于 URL
        del query_params['app_id']

        # 调用 client 的 post 方法发送请求
        return MetaListResult(self.get(url, query=query_params))

    def table_meta(self, query_params):
        if 'app_id' not in query_params:
            raise ValueError("Missing required parameter: 'app_id'")

        if 'api_name' not in query_params:
            raise ValueError("Missing required parameter: 'api_name'")
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{query_params["app_id"]}/tables/{query_params["api_name"]}'

        # 移除 app_id，因为它已经被用于 URL
        del query_params['app_id']
        del query_params['api_name']

        # 调用 client 的 post 方法发送请求
        return MetaResult(self.get(url, query=query_params))
