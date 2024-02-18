import time
from websockets.server import serve
import asyncio
import websockets
import threading
import asyncio
from ..vrobots_msgs.python.states_generated import StatesMsg
from ..vrobots_msgs.python.empty_generated import EmptyMsg
from ..vrobots_msgs.python.commands_generated import CommandMsg


class WebSocketList(list):
    def __init__(self, *args):
        super().__init__(args)


ws_list = WebSocketList()


class NamedWebsocket:
    def __init__(self, name, ws) -> None:
        self.ws = ws
        self.name = name
        self.msg = None

    def handle_new_msg(self, name, ws):
        if name is None or self.name != name:
            return
        self.handle_dup(ws)

    def handle_dup(self, ws):
        if self.validate_dup(ws) is True:
            return
        else:
            self.ws.close()
            self.ws = ws

    def validate_dup(self, ws):
        if self.ws is ws:
            return True
        else:
            return False

    def remove(self):
        print(f"Removing {self.name} from ws_list")
        ws_list.remove(self)


def get_name_from_msg(msg):

    if StatesMsg.StatesMsgBufferHasIdentifier(msg, 0) is True:
        robots_all = StatesMsg.GetRootAsStatesMsg(msg)
        name = robots_all.Name().decode("utf-8")
        return name

    if CommandMsg.CommandMsgBufferHasIdentifier(msg, 0) is True:
        cmd = CommandMsg.GetRootAsCommandMsg(msg)
        name = cmd.Name().decode("utf-8")
        return name

    return None


def upsert_ws_list(name, ws):
    # check if ws_list has name
    for named_ws in ws_list:
        if named_ws.name == name:
            named_ws.handle_new_msg(name, ws)
            return

    # if new, push
    named_ws = NamedWebsocket(name, ws)
    ws_list.append(named_ws)
    named_ws.handle_new_msg(name, ws)


def remove_ws_list(name):
    for named_ws in ws_list:
        if named_ws.name == name:
            named_ws.remove()
            return


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

            for named_ws in ws_list:
                print(f"ws_list: {named_ws.name}")
                if named_ws.name == name:
                    continue
                # print(len(WebSocketList))
                try:
                    print(f"sending to {named_ws.name} from {name}")
                    await named_ws.ws.send(message)
                except Exception as e:
                    # print(f"Error while sending message: {message} to {named_ws.name}")
                    remove_ws_list(named_ws.name)

    except Exception as e:
        print(f"Error while processing message: {message}")
        print(e)


def run_bridge_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("simulator server running @ 12740")
    start_server = websockets.serve(echo, "0.0.0.0", 12740)

    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
    loop.run_until_complete(start_server)
    loop.run_forever()


class BridgeModule:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BridgeModule, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.stopFlag = False
        self.thread = None
        self.value = 1

    def start(self):
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stopFlag = True
        self.thread.join()

    def loop(self):
        while self.stopFlag == False:
            run_bridge_server()


BRIDGE = BridgeModule()


async def main():
    async with serve(echo, "localhost", 12740):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    run_bridge_server()  # run without gui
