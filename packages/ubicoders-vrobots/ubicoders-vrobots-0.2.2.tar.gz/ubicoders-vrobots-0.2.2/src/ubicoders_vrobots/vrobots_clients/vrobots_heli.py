import flatbuffers
from .msg_helper import VRobotState
from ..vrobots_msgs.python.states_generated import *
from ..vrobots_msgs.python.commands_generated import *
from .clientutils import VirtualRobot, System


class Helicopter2D(VirtualRobot):
    def __init__(self) -> None:
        self.states = VRobotState(None)
        self.force = 0

    def pack_cmd_force(self) -> bytes:
        builder = flatbuffers.Builder(512)
        sender = builder.CreateString("python")
        CommandMsgStart(builder)
        CommandMsgAddName(builder, sender)
        CommandMsgAddId(builder, 20)
        CommandMsgAddFloatVal(builder, self.force)
        os = CommandMsgEnd(builder)
        builder.Finish(os, b"CMD0")
        return builder.Output()

    def pack_cmd_reset(self) -> bytes:
        builder = flatbuffers.Builder(512)
        sender = builder.CreateString("python")
        CommandMsgStart(builder)
        CommandMsgAddName(builder, sender)
        CommandMsgAddId(builder, 100)
        os = CommandMsgEnd(builder)
        builder.Finish(os, b"CMD0")
        return builder.Output()

    def pack_setup(self) -> List[bytes]:
        return []

    def pack(self) -> List[bytes]:
        cmd_force = self.pack_cmd_force()
        return [cmd_force]

    def unpack(self, msg):  # FB_MultirotorMsgAll
        objdata = StatesMsgT.InitFromPackedBuf(msg, 0)
        name = objdata.name.decode("utf-8")
        if (name is not None) and (name != "heli"):
            return
        self.states = VRobotState(objdata)
        # ## TODO onboard pid params


# ===============================================================================
# dev code
# ===============================================================================

heli = Helicopter2D()


class UbicodersMain:
    def __init__(self) -> None:
        pass

    def setup(self):
        # mr.mass = 2 kg
        pass

    def loop(self):
        states = heli.states
        print(states.lin_pos)
        print(states.lin_vel)

        heli.force = 20


if __name__ == "__main__":
    sys = System(heli, UbicodersMain())
    sys.start()
