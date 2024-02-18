import flatbuffers
from .msg_helper import VRobotState
from ..vrobots_msgs.python.states_generated import *
from ..vrobots_msgs.python.commands_generated import *
from .clientutils import VirtualRobot, System


class InertialSensor(VirtualRobot):
    def __init__(self) -> None:
        self.states = VRobotState(None)

    def pack_cmd_0(self) -> bytes:
        pass
        # builder = flatbuffers.Builder(512)
        # sender = builder.CreateString("python")
        # CommandMsgStart(builder)
        # CommandMsgAddName(builder, sender)
        # CommandMsgAddId(builder, 0)
        # os = CommandMsgEnd(builder)
        # builder.Finish(os, b"CMD0")
        # return builder.Output()

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
        cmd_reset = self.pack_cmd_reset()
        return [cmd_reset]

    def pack(self) -> List[bytes]:
        # cmd0 = self.pack_cmd_0()
        return []

    def unpack(self, msg):  # FB_MultirotorMsgAll
        objdata = StatesMsgT.InitFromPackedBuf(msg, 0)
        name = objdata.name.decode("utf-8")
        if (name is not None) and (name != "imu0"):
            return
        self.states = VRobotState(objdata)
        # ## TODO onboard pid params


# ===============================================================================
# dev code
# ===============================================================================

imu = InertialSensor()


class UbicodersMain:
    def __init__(self) -> None:
        pass

    def setup(self):
        # mr.mass = 2 kg
        pass

    def loop(self):
        states = imu.states
        # print(states.accelerometer)
        # print(states.gyroscope)
        # print(states.euler)


if __name__ == "__main__":
    sys = System(imu, UbicodersMain())
    sys.start()
