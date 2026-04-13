from fourier_core.config.fi_config import gl_config

from fourier_grx.process.sync.fi_sync_server_zenoh import SyncServerZenoh
from fourier_grx.process.sync.fi_sync_server_socket import SyncServerSocket
from fourier_grx.process.sync.fi_sync_server_zmq import SyncServerZMQ

if gl_config.parameters.get("communication", {}).get("type", None) == "zenoh":
    SyncServer = SyncServerZenoh
elif gl_config.parameters.get("communication", {}).get("type", None) == "socket":
    SyncServer = SyncServerSocket
elif gl_config.parameters.get("communication", {}).get("type", None) == "zmq":
    SyncServer = SyncServerZMQ
else:
    # 默认使用 zenoh 通信
    SyncServer = SyncServerZenoh
