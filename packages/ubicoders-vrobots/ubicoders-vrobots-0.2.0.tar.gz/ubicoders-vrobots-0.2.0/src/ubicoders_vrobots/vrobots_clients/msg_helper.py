from ..vrobots_msgs.python.states_generated import (
    Vec3MsgT,
    Vec4MsgT,
    StatesMsgT,
)

import json


class Vec4(Vec4MsgT):
    def __init__(self, instance: Vec4MsgT):
        super().__init__()
        if instance == None:
            self.x = 0
            self.y = 0
            self.z = 0
            self.w = 0
            return
        self.x = instance.x
        self.y = instance.y
        self.z = instance.z
        self.w = instance.w

    def get_dict_data(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "w": self.w,
        }

    def __str__(self) -> str:
        return json.dumps(self.get_dict_data(), indent=4, sort_keys=True)


class Vec3(Vec3MsgT):
    def __init__(self, instance: Vec3MsgT):
        super().__init__()
        if instance == None:
            self.x = 0
            self.y = 0
            self.z = 0
            return
        self.x = instance.x
        self.y = instance.y
        self.z = instance.z

    def get_dict_data(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def __str__(self) -> str:
        return json.dumps(self.get_dict_data(), indent=4, sort_keys=True)


class VRobotState(StatesMsgT):
    def __init__(self, instance: StatesMsgT) -> None:
        if instance == None:
            self.name = ""
            self.timestamp = 0

            self.lin_acc = Vec3(None)
            self.lin_vel = Vec3(None)
            self.lin_pos = Vec3(None)

            self.ang_acc = Vec3(None)
            self.ang_vel = Vec3(None)
            self.euler = Vec3(None)
            self.euler_dot = Vec3(None)
            self.quaternion = Vec4(None)

            self.pwm = None
            self.force = Vec3(None)
            self.torque = Vec3(None)

            self.accelerometer = Vec3(None)
            self.gyroscope = Vec3(None)
            self.magnetometer = Vec3(None)
            return

        self.name = instance.name.decode("utf-8")
        self.timestamp = instance.timestamp
        self.lin_acc = Vec3(instance.linAcc)
        self.lin_vel = Vec3(instance.linVel)
        self.lin_pos = Vec3(instance.linPos)
        self.ang_acc = Vec3(instance.angAcc)
        self.ang_vel = Vec3(instance.angVel)
        self.euler = Vec3(instance.euler)
        self.euler_dot = Vec3(instance.eulerDot)
        self.quaternion = Vec4(instance.quaternion)
        self.pwm = instance.pwm
        self.force = Vec3(instance.force)
        self.torque = Vec3(instance.torque)
        self.accelerometer = Vec3(instance.accelerometer)
        self.gyroscope = Vec3(instance.gyroscope)
        self.magnetometer = Vec3(instance.magnetometer)

    def get_dict_data(self):
        return {
            "name": self.name,
            "timestamp": self.timestamp,
            "lin_acc": self.lin_acc.get_dict_data(),
            "lin_vel": self.lin_vel.get_dict_data(),
            "lin_pos": self.lin_pos.get_dict_data(),
            "ang_acc": self.ang_acc.get_dict_data(),
            "ang_vel": self.ang_vel.get_dict_data(),
            "euler": self.euler.get_dict_data(),
            "euler_dot": self.euler_dot.get_dict_data(),
            "quaternion": self.quaternion.get_dict_data(),
            "pwm": self.pwm.tolist() if self.pwm is not None else "",
            "force": self.force.get_dict_data(),
            "torque": self.torque.get_dict_data(),
            "accelerometer": self.accelerometer.get_dict_data(),
            "gyroscope": self.gyroscope.get_dict_data(),
            "magnetometer": self.magnetometer.get_dict_data(),
        }

    def __str__(self) -> str:
        return json.dumps(self.get_dict_data(), indent=4, sort_keys=True)
