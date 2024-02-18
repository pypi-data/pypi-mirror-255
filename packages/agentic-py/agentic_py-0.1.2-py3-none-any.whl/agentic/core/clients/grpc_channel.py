import grpc
import asyncio


ADDRESS = "localhost:50051"

_channel = None


async def get_channel():
    global _channel
    if _channel is None:
        _channel = grpc.aio.insecure_channel(ADDRESS)
        try:
            await asyncio.wait_for(_channel.channel_ready(), timeout=10.0)
        except asyncio.TimeoutError:
            raise Exception(f"Coordinator server is not available at {ADDRESS}")
    return _channel
