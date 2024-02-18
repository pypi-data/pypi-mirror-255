from abc import ABC, abstractmethod
import websocket
import time
import _thread


class WebsocketClient:
    def __init__(self, robot) -> None:
        self.robot = robot

        def on_message(ws, message):
            # print("message recieved")
            # print(message)
            self.robot.unpack(message)

        def on_error(ws, error):
            print(error)

        def on_close(ws, close_status_code, close_msg):
            print("### closed ###")

        def on_open(ws):
            print("Opened connection")

            ## setup and send setup message
            self.robot.setup()
            byte_msg_list = self.robot.pack_setup()
            [ws.send(byte_msg, opcode=0x2) for byte_msg in byte_msg_list]

            def _update_loop(*args):
                while True:
                    time.sleep(0.02)  # 50 hz
                    self.robot.loop()
                    byte_msg_list = self.robot.pack()
                    [ws.send(byte_msg, opcode=0x2) for byte_msg in byte_msg_list]
                    # ws.send("hello server")

            _thread.start_new_thread(_update_loop, ())

        self.ws = websocket.WebSocketApp(
            "ws://localhost:12740",
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_message=on_message,
        )

    def start(self):
        self.ws.run_forever()


class VirtualRobot(ABC):
    def __init__(self) -> None:
        self.setup = None
        self.loop = None

    # Returns a list of byte messages that contains FBs
    @abstractmethod
    def pack_setup(self) -> [bytes]:
        pass

    # Returns a list of byte messages that contains FBs
    @abstractmethod
    def pack(self) -> [bytes]:
        pass

    # Unpacks the message and updates the robot state
    @abstractmethod
    def unpack(self):
        pass


class System:
    def __init__(
        self, robot, ubicoders_main_obj, duration=5, stop_condition=None
    ) -> None:
        self.robot = robot
        self.robot.setup = ubicoders_main_obj.setup
        self.robot.loop = ubicoders_main_obj.loop
        self.ws = WebsocketClient(self.robot)

    def start(self):
        self.ws.start()


if __name__ == "__main__":
    sys = System()
