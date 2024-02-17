import json
import time
from loguru import logger
from jupyter_server.gateway.managers import GatewayKernelClient, url_path_join, url_escape
from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_server.gateway.gateway_client import GatewayClient
from jupyter_core.utils import ensure_async
from threading import Thread
import websocket
class ServerlessGatewayKernelClient(GatewayKernelClient):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def start_channels(self, shell=True, iopub=True, stdin=True, hb=True, control=True,retry=0):
            """Starts the channels for this kernel.
            For this class, we establish a websocket connection to the destination
            and set up the channel-based queues on which applicable messages will
            be posted.
            """
            ws_url = url_path_join(
                GatewayClient.instance().ws_url or "",
                GatewayClient.instance().kernels_endpoint,
                url_escape(self.kernel_id),
                "channels",
            )
            # Gather cert info in case where ssl is desired...
            ssl_options = {
                "ca_certs": GatewayClient.instance().ca_certs,
                "certfile": GatewayClient.instance().client_cert,
                "keyfile": GatewayClient.instance().client_key,
            }
            headers = json.loads(GatewayClient.instance().headers)

            ## known issue: connection timeout on the first try
            ## workaround: retry more then once
            connected = False and retry == 0
            while not connected:
                try:
                    self.channel_socket = websocket.create_connection(
                        ws_url,
                        timeout=5,
                        enable_multithread=True,
                        sslopt=ssl_options,
                        header=headers,
                    )
                    connected = True
                    logger.info(f"Connected to kernel: {self.kernel_id}")
                except Exception as e:
                    if retry == 10:
                        logger.error(f"Failed to connect to kernel: e: {e}")
                        raise e
                    time.sleep(0.5)
                    retry += 1


            await ensure_async(
                    AsyncKernelClient.start_channels(self, shell=shell, iopub=iopub, stdin=stdin, hb=hb, control=control)
            )
            self.response_router = Thread(target=self._route_responses)
            self.response_router.start()
        
    async def is_alive(self):
        """Is the kernel process still running?"""
        try:
            self.channel_socket.ping()
            return True
        except Exception as e:
            logger.error(f"Failed to ping kernel: e: {e}")
            raise e