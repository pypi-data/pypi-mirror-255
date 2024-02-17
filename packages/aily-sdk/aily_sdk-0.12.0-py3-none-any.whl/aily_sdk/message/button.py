class Button:
    def __init__(self, btn_type="default", width="default", action="navigate", url="", message="", skill="",
                 text="按钮文案"):
        self.btn_type = btn_type
        self.width = width
        self.action = action
        self.url = url
        self.message = message
        self.skill = skill
        self.text = text

    def to_message(self):
        # 构建按钮配置字符串
        button_config = f'<button \n  type="{self.btn_type}"\n'

        # 宽度配置
        button_config += f'  width="{self.width}"\n'

        # 添加行动、URL、消息和技能配置
        button_config += f'  action="{self.action}"\n'
        if self.url:
            button_config += f'  url="{self.url}"\n'
        if self.message:
            button_config += f'  message="{self.message}"\n'
        if self.skill:
            button_config += f'  skill="{self.skill}"\n'

        # 结束标签和按钮文案
        button_config += f'>\n{self.text}\n</button>'

        return button_config



