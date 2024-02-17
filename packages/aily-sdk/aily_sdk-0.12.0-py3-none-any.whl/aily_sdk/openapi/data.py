import json

from aily_sdk.openapi import OpenAPIClient


class DataResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.has_more = None
        self.total = None
        self.records = []
        if 'data' in result:
            self.has_more = result['data']['has_more']
            self.total = result['data']['total']
            self.records = json.loads(result['data']['records'])


class SQLDataResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.sql = None
        self.column_names = None
        self.records = []
        if 'data' in result:
            self.column_names = result['data']['column_names']
            self.sql = result['data']['sql']
            self.records = json.loads(result['data']['records'])


class OperationResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.items = []
        if 'data' in result:
            self.items = result['data']['items']


class DataClient(OpenAPIClient):
    def query(self, query_params):
        # 检查必要的参数是否存在
        if 'app_id' not in query_params:
            raise ValueError("Missing required parameter: 'app_id'")

        # 构建请求的 URL
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{query_params["app_id"]}/records'

        # 移除 app_id，因为它已经被用于 URL
        del query_params['app_id']

        # 调用 client 的 post 方法发送请求
        return DataResult(self.get(url, data=query_params))

    def query_sql(self, query_params):
        """
        :param query_params: {

            "query": "SELECT id FROM 'dataset_a' LIMIT 10",
            "option": {
                "stringify_number": false,
                "normalize_column_name": false
            },
            "table_type": "dataset_name"
        }
        :return:
        """
        if 'app_id' not in query_params:
            raise ValueError("Missing required parameter: 'app_id'")

        # 构建请求的 URL
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{query_params["app_id"]}/records/query'

        # 移除 app_id，因为它已经被用于 URL
        del query_params['app_id']

        # 调用 client 的 post 方法发送请求
        return SQLDataResult(self.post(url, data=query_params))

    def write(self, data):
        # 构建请求的 URL
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{data["app_id"]}/records/batch_upsert'

        # 移除 app_id，因为它已经被用于 URL
        del data['app_id']
        data['records'] = json.dumps(data['records'])
        # 调用 client 的 post 方法发送请求
        return OperationResult(self.post(url, data=data))

    def remove(self, data):
        # 构建请求的 URL
        url = f'https://open.feishu.cn/open-apis/aily/v1/apps/{data["app_id"]}/records/batch_remove'

        # 移除 app_id，因为它已经被用于 URL
        del data['app_id']
        data['records'] = json.dumps(data['records'])
        # 调用 client 的 post 方法发送请求
        return OperationResult(self.post(url, data=data))
