from fourier_core.config.fi_config import gl_config

from fourier_grx.process.sync.fi_sync_client_zenoh import SyncClientZenoh
from fourier_grx.process.sync.fi_sync_client_socket import SyncClientSocket
from fourier_grx.process.sync.fi_sync_client_zmq import SyncClientZMQ

if gl_config.parameters.get("communication", {}).get("type", None) == "zenoh":
    SyncClient = SyncClientZenoh
elif gl_config.parameters.get("communication", {}).get("type", None) == "socket":
    SyncClient = SyncClientSocket
elif gl_config.parameters.get("communication", {}).get("type", None) == "zmq":
    SyncClient = SyncClientZMQ
else:
    # 默认使用 zenoh 通信
    SyncClient = SyncClientZenoh
