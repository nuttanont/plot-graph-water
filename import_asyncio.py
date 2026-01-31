import asyncio
import websockets
import json

async def listen():
    uri = "wss://telerid.rid.go.th/ws/station/703/"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            print(data)

asyncio.run(listen())