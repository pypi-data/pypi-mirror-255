from dataclasses import dataclass
import json


@dataclass
class ChannelContextData:
    sender_id: str
    chat_id: str
    chat_type: str
    message_id: str


def parse_channel_context(channel_context: str, mock_data: dict = None) -> ChannelContextData:
    if mock_data is None:
        mock_data = {}

    cc = json.loads(channel_context)
    return ChannelContextData(
        sender_id=cc.get('sender_id', mock_data.get('sender_id', 'developer_id')),
        chat_id=cc.get('chat_id', mock_data.get('chat_id')),
        chat_type=cc.get('chat_type', mock_data.get('chat_type')),
        message_id=cc.get('message_id', mock_data.get('message_id')),
    )
