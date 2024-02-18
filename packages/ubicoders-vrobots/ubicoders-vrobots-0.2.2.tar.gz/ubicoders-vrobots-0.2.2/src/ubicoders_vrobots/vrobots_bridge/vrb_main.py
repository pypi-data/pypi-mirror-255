import threading
from .vr_ws_srv import run_bridge_server
from .vr_rest_srv import run_server


def start_servers(task_pair_list):
    threads = []
    for task_pair in task_pair_list:
        t = threading.Thread(target=task_pair["target"], args=task_pair["args"])
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        
def vrb_main():
    task_pair_list = [
        {
            "target": run_bridge_server,
            "args": (12740,)
        },
        {
            "target": run_server,
            "args": (12741,)
        }
    ]
    start_servers(task_pair_list)        


if __name__ == "__main__":
    vrb_main()
