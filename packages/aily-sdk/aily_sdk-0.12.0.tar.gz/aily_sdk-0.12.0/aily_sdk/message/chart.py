from typing import List, Dict, Union


# 定义基础图表规格
class BaseChart:
    def __init__(self, data, x_field: Union[str, List[str]], y_field: Union[str, List[str]], series_field: str = None,
                 stack: bool = False):
        self.data = data
        self.type = None
        self.x_field = x_field
        self.y_field = y_field
        self.series_field = series_field
        self.stack = stack

    def to_data_string(self):
        data_str = "      values: [\n"
        for item in self.data:
            data_str += "        {" + ", ".join(
                [f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}" for k, v in item.items()]) + "},\n"
        data_str += "      ]\n"
        return data_str

    @staticmethod
    def format_field(field):
        if isinstance(field, str):
            return f"'{field}'"
        elif isinstance(field, list):
            return '[' + ', '.join(f"'{f}'" for f in field) + ']'

    def to_chart_string(self, dataIndex):
        x_field_str = self.format_field(self.x_field)
        y_field_str = self.format_field(self.y_field)

        parts = [
            f"type: '{self.type}'",
            f"dataIndex: {dataIndex}",
            f"xField: {x_field_str}",
            f"yField: {y_field_str}"
        ]

        # 仅当 series_field 不为 None 时添加
        if self.series_field is not None:
            parts.append(f"seriesField: '{self.series_field}'")

        chart_str = "{\n  " + ",\n  ".join(parts) + "\n},\n"
        return chart_str

    def to_message(self):
        x_field_str = self.format_field(self.x_field)
        y_field_str = self.format_field(self.y_field)

        chart_str = f"<chart chartSpec={{\n"
        chart_str += f"  type: '{self.type}',\n"
        chart_str += "  data: {\n    values: [\n"
        for item in self.data:
            chart_str += "      {" + ", ".join(
                [f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}" for k, v in item.items()]) + "},\n"
        chart_str += "    ]\n  },\n"
        chart_str += f"  xField: {x_field_str},\n"
        chart_str += f"  yField: {y_field_str},\n"
        if self.series_field:
            chart_str += f"  seriesField: '{self.series_field}'\n"
        chart_str += "}/>"
        return chart_str


# 定义线图规格
class LineChart(BaseChart):
    def __init__(self, data, x_field: Union[str, List[str]], y_field: Union[str, List[str]], series_field: str = None,
                 stack: bool = False):
        super().__init__(data, x_field, y_field, series_field, stack)
        self.type = 'line'


# 定义区域图规格
class AreaChart(BaseChart):
    def __init__(self, data, x_field: Union[str, List[str]], y_field: Union[str, List[str]], series_field: str = None,
                 stack: bool = False):
        super().__init__(data, x_field, y_field, series_field, stack)
        self.type = 'area'


# 定义条形图规格
class BarChart(BaseChart):
    def __init__(self, data, x_field: Union[str, List[str]], y_field: Union[str, List[str]], series_field: str = None,
                 stack: bool = False):
        super().__init__(data, x_field, y_field, series_field, stack)
        self.type = 'bar'


# 定义饼图规格
class PieChart:
    def __init__(self, data, value_field: Union[str, List[str]], category_field: str):
        self.data = data
        self.type = 'pie'
        self.value_field = value_field
        self.category_field = category_field

    @staticmethod
    def format_field(field):
        if isinstance(field, str):
            return f"'{field}'"
        elif isinstance(field, list):
            return '[' + ', '.join(f"'{f}'" for f in field) + ']'

    def to_message(self):
        value_field_str = self.format_field(self.value_field)
        category_field_str = self.format_field(self.category_field)

        chart_str = f"<chart chartSpec={{\n"
        chart_str += f"  type: '{self.type}',\n"
        chart_str += "  data: {\n    values: [\n"
        for item in self.data:
            chart_str += "      {" + ", ".join(
                [f"{k}: '{v}'" if isinstance(v, str) else f"{k}: {v}" for k, v in item.items()]) + "},\n"
        chart_str += "    ]\n  },\n"
        chart_str += f"  valueField: {value_field_str},\n"
        chart_str += f"  categoryField: {category_field_str},\n"
        chart_str += "}/>"
        return chart_str


# 定义通用图表规格
class CommonChart:
    def __init__(self, charts: [LineChart, BarChart, AreaChart]):
        self.type = 'common'
        self.charts = charts

    def to_message(self):
        chart_str = "<chart chartSpec={\n"
        chart_str += "  type: 'common',\n"
        chart_str += "  data: [\n"
        for i, chart in enumerate(self.charts):
            chart_str += "    {\n"
            chart_str += chart.to_data_string()
            chart_str += "    },\n" if i < len(self.charts) - 1 else "    }\n"
        chart_str += "  ],\n"
        chart_str += "  series: ["
        for i, chart in enumerate(self.charts):
            chart_str += chart.to_chart_string(i)
        chart_str += "  ]\n"
        chart_str += "}/>"
        return chart_str
