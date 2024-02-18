import asyncio
import websockets
import asyncio
from ..vrobots_msgs.python.empty_generated import EmptyMsg
from .ws_utils import (
    get_name_from_msg,
    WSList,
    upsert_ws_list,
    remove_ws_list,
)


async def echo(websocket):
    name = None
    try:
        async for message in websocket:
            if EmptyMsg.EmptyMsgBufferHasIdentifier(message, 0) is True:
                continue

            name = get_name_from_msg(message)
            if name is None:
                continue
            # print(f"Client connected: {name}")

            upsert_ws_list(name, websocket)

            for named_ws in WSList:
                # print(f"ws_list: {named_ws.name}")
                if named_ws.name == name:
                    continue
                # print(len(WebSocketList))
                try:
                    # print(f"sending to {named_ws.name} from {name}")
                    await named_ws.ws.send(message)
                except Exception as e:
                    # print(f"Error while sending message: {message} to {named_ws.name}")
                    remove_ws_list(named_ws.name)

    except Exception as e:
        print(f"Error while processing message: {message}")
        print(e)


def run_bridge_server(port=12740):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print(f"\033[92mVirtual Robots Bridge is running @ port {port}\033[0m")
    start_server = websockets.serve(echo, "0.0.0.0", port)
    loop.run_until_complete(start_server)
    loop.run_forever()




if __name__ == "__main__":
    run_bridge_server()
