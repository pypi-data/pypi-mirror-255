
import asyncio
import uuid
import papermill as pm
from loguru import logger
from .kernels.kernel_manager import ServerlessMixingKernelManager
from jupyter_server.gateway.gateway_client import GatewayClient

from tornado.escape import json_decode
from jupyter_server.gateway.gateway_client import gateway_request
from jupyter_server.utils import url_path_join
from dataproc_jupyter_plugin.handlers import get_cached_credentials
from google.cloud.jupyter_config.config import gcp_kernel_gateway_url
from papermill.iorw import papermill_io

from paperless.constants import *
from paperless.notebook import notebook_manager
from paperless.serverless import serverless_manager

class Paperless():
    """
    Represents an interactive session for executing notebooks using a serverless environment.

    Args:
        notebook_path (str): The path to the notebook file.

    Attributes:
        papermill_io: The papermill IO instance.
        notebook_path (str): The path to the notebook file.
        notebook: The notebook object.
        sessionid (str): The session ID.
        kernel_name (str): The kernel name.
        session_template (str): The session template.
        crad: The cached credentials.

    Methods:
        __init__: Initializes the InteractiveSession instance.
        configure: Configures the gateway client with the necessary settings.
        wait_for_session: Waits for the session to be available and saves the notebook with session metadata.
        verify: Verifies the session by getting the kernel spec and preparing the kernel.
        execute: Executes the notebook.
        shutdown: Shuts down the session.
        get_kernel_spec: Gets the kernel spec.
        prepare_the_kernel: Prepares the kernel.
    """

    def __init__(self, notebookPath=None,templateName=None):
        logger.debug("starting interactive session", notebookPath)
        self.papermill_io = papermill_io
        self.notebook_path = notebookPath
        self.notebook = notebook_manager.read_notebook(notebookPath)

        metadata = self.notebook['metadata']
        
        # get session id from notebook metadata
        if METADATA_KEY in metadata and  serverless_manager.\
            is_session_active_and_ready(metadata[METADATA_KEY]["session_id"]):
            logger.debug("found metadata in notebook: ", metadata[METADATA_KEY])
            self.sessionid = metadata[METADATA_KEY]["session_id"]
            self.kernel_name = metadata[METADATA_KEY]["kernel_name"]
            self.session_template = metadata[METADATA_KEY]["session_template"]
            self.session_exists = True
            self.session_ready = False
        else:
            logger.debug("no metadata found in notebook, generating new session")
            self.sessionid = str(uuid.uuid4())
            self.kernel_name =  f"paperless-{self.sessionid}"

            if templateName is not None:
                self.session_template =  serverless_manager.build_session_template(templateName)
            else: 
                serverless_manager.build_session_template()
            self.notebook['metadata'][METADATA_KEY] = {"session_id": self.sessionid, "kernel_name": self.kernel_name, "session_template": self.session_template}
            notebook_manager.save_notebook(self.notebook, self.notebook_path)
            logger.debug("saved new notebook with metadata")
            self.session_exists = False
            self.session_ready = False

        self.crad = get_cached_credentials(log=None)
        logger.debug("got credentials - ready", self.crad)

    def configure(self):
        """
        Configures the gateway client with the necessary settings.

        Returns:
            self: The current instance of the InteractiveSession class.
        """
        logger.debug("configuring gateway client")
        GatewayClient.instance().url = gcp_kernel_gateway_url() 
        GatewayClient.instance().kernel_ws_protocol=""
        GatewayClient.instance().auth_scheme = 'Bearer'
        GatewayClient.instance().auth_token = self.crad["access_token"]
        GatewayClient.instance().headers = '{"Cookie": "_xsrf=XSRF", "X-XSRFToken": "XSRF","authorization":"Bearer ' + self.crad["access_token"] + '"}'
        logger.debug("configured gateway client")
        return self

    def wait_for_session(self):
        """
        Waits for the session to be available and saves the notebook with session metadata.

        Returns:
            self: The current instance of the InteractiveSession class.
        """
        ## getting session
        logger.debug("waiting for session")
        if not self.session_exists:
            serverless_manager.create_session(sessionid=self.sessionid, templateName=self.session_template)
        logger.debug("session created")
        return self

    def verify(self):
        """
        Verifies the session by getting the kernel spec and preparing the kernel.

        Returns:
            self: The current instance of the InteractiveSession class.
        """
        asyncio.run(self.get_kernel_spec())
        asyncio.run(self.prepare_the_kernel())
        return self

    def execute(self, *args, **kwargs):
        """
        Executes the notebook.

        Returns:
            self: The current instance of the InteractiveSession class.
        """

        kwargs = { **kwargs ,** { 'input_path': self.notebook_path } }
        kwargs = { **kwargs ,** {'output_path': self.notebook_path.replace('.ipynb','-out.ipynb')} }
        kwargs = { **kwargs ,** { 'kernel_name': self.kernel_spec["default"]} }
        kwargs = { **kwargs ,** { 'km': ServerlessMixingKernelManager(c_kernel=self.kernel, c_kernel_spec=self.kernel_spec) } }
        kwargs = { **kwargs ,** { 'kc': self.kernel} }
        pm.execute_notebook(**kwargs)
        return self
    
    def shutdown(self):
        """
        Shuts down the session.
        """
        # serverless_manager.delete_session(sessionid=self.sessionid)
        # sys.exit()

    async def get_kernel_spec(self):
        """
        Gets the kernel spec.
        """
        kernelspec_url = url_path_join(GatewayClient.instance().url, GatewayClient.instance().kernelspecs_endpoint)
        response = await gateway_request(
            kernelspec_url,
            method="GET",
            headers={"Content-Type": "application/json"},
        )
        self.kernel_spec =  json_decode(response.body)
        logger.debug(self.kernel_spec)
        return self.kernel_spec

    async def prepare_the_kernel(self):
        """
        Prepares the kernel.
        """
        kernels_url = url_path_join(GatewayClient.instance().url, GatewayClient.instance().kernels_endpoint)
        response = await gateway_request(
            kernels_url,
            method="GET",
            headers={"Content-Type": "application/json"},
        )
        self.kernel = json_decode(response.body)
        logger.debug(self.kernel)
        return self.kernel
        
 
