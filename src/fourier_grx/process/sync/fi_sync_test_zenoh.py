import time
import argparse

from threading import Thread

from fi_sync_server_zenoh import SyncServerZenoh
from fi_sync_client_zenoh import SyncClientZenoh


def server_test(period: float = 60.0):
    server = SyncServerZenoh()

    count = 0
    while count < period:
        # 定时发布测试数据
        server.publish(key="comm", value={"msg": f"Hello from server {count}"})
        print(f"[Server] Published message {count} at {time.time()}")
        count += 1
        time.sleep(1)


def client_test(period: float = 60.0):
    client = SyncClientZenoh()

    count = 0
    while count < period:
        # 发送数据到 server
        client.publish(key="comm", value={"msg": f"Hello from client {count}"})
        print(f"[Client] Published message {count} at {time.time()}")
        count += 1
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test SyncServerZenoh / SyncClientZenoh")
    parser.add_argument("--mode",
                        choices=["server", "client", "both"],
                        default="both",
                        help="启动模式：server / client / both")
    parser.add_argument("--period",
                        type=float,
                        default=60.0,
                        help="测试持续时间（秒）")
    args = parser.parse_args()

    threads = []

    if args.mode in ["server", "both"]:
        server_thread = Thread(target=server_test, args=(args.period,), daemon=True)
        server_thread.start()
        threads.append(server_thread)

    if args.mode in ["client", "both"]:
        client_thread = Thread(target=client_test, args=(args.period,), daemon=True)
        client_thread.start()
        threads.append(client_thread)

    # 等待所有线程结束
    for t in threads:
        t.join()
