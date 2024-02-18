from ..vrobots_msgs.python.states_generated import StatesMsg
from ..vrobots_msgs.python.empty_generated import EmptyMsg
from ..vrobots_msgs.python.commands_generated import CommandMsg


class WebSocketList(list):
    def __init__(self, *args):
        super().__init__(args)


WSList = WebSocketList()


class NamedWebsocket:
    def __init__(self, name, ws) -> None:
        self.ws = ws
        self.name = name

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
        WSList.remove(self)


def upsert_ws_list(name, ws):
    # check if ws_list has name
    for named_ws in WSList:
        if named_ws.name == name:
            named_ws.handle_new_msg(name, ws)
            return

    # if new, push
    print(f"{name} connected.")
    named_ws = NamedWebsocket(name, ws)
    WSList.append(named_ws)
    named_ws.handle_new_msg(name, ws)


def remove_ws_list(name):
    for named_ws in WSList:
        if named_ws.name == name:
            print(f"{name} disconnected.")
            named_ws.remove()
            return


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
