from typing import List

from agentic.proto import chat_pb2

from agentic.core.clients.chat_client import ChatClient


class Chat:
    @classmethod
    async def create(cls, name: str):
        client = ChatClient()
        chat_id = await client.create_chat(name)
        return cls(chat_id)

    def __init__(self, chat_id: str):
        self._client = ChatClient()
        self._chat_id = chat_id

    def __eq__(self, __value: object) -> bool:
        return self._chat_id == getattr(__value, "_chat_id", None)

    @property
    def chat_id(self):
        return self._chat_id

    async def get_messages(self) -> List[chat_pb2.Message]:
        return await self._client.get_messages(self._chat_id)

    async def add_message(
        self,
        msg: chat_pb2.Message,
    ):
        res = await self._client.add_message(self._chat_id, msg)
        return res.message.id

    async def update_message(
        self,
        msg: chat_pb2.Message,
    ):
        await self._client.update_message(msg)
