from typing import List, Dict, Optional

import traceback

import json

from agentic.proto import chat_pb2_grpc, chat_pb2

from .grpc_channel import get_channel


DEFAULT_TIMEOUT = 30


class ChatClient:
    @property
    async def _stub(self) -> chat_pb2_grpc.ChatServiceStub:
        channel = await get_channel()
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        return stub

    async def create_chat(
        self,
        name: str,
    ) -> str:
        stub = await self._stub
        response = await stub.CreateChat(
            chat_pb2.CreateChatRequest(
                name=name,
            ),
            timeout=DEFAULT_TIMEOUT,
        )
        return response.chat.id

    async def get_messages(
        self,
        chat_id: str,
    ) -> List[chat_pb2.Message]:
        stub = await self._stub
        response = await stub.GetChat(
            chat_pb2.GetChatRequest(
                chat_id=chat_id,
            ),
            timeout=DEFAULT_TIMEOUT,
        )
        return response.messages

    async def add_message(
        self,
        chat_id: str,
        msg: chat_pb2.Message,
    ) -> chat_pb2.AddMessageResponse:
        stub = await self._stub
        return await stub.AddMessage(
            chat_pb2.AddMessageRequest(
                chat_id=chat_id,
                message=msg,
            ),
            timeout=DEFAULT_TIMEOUT,
        )

    async def update_message(
        self,
        msg: chat_pb2.Message,
    ) -> None:
        stub = await self._stub
        await stub.UpdateMessage(
            chat_pb2.UpdateMessageRequest(
                message=msg,
            ),
            timeout=DEFAULT_TIMEOUT,
        )
