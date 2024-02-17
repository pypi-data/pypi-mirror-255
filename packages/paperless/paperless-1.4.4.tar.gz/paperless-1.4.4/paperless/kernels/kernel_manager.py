from kernels_mixer.kernels import MixingKernelManager, MixingKernelSpecManager
from .kernel_client import ServerlessGatewayKernelClient


class ServerlessMixingKernelManager(MixingKernelManager):

    def __init__(self, c_kernel, c_kernel_spec,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kernel_id = c_kernel[0]['id']
        self.kernel_name = c_kernel_spec['default']
        self.remote_manager =  ServerlessGatewayKernelClient(
            kernel_id=self.kernel_id ,
            parent=self,
            log=self.log,
            connection_file=self.connection_file,
            kernel_spec_manager=MixingKernelSpecManager(*args, **kwargs))
        MixingKernelManager._kernel_id_map[self.kernel_name] = self.kernel_name 


    async def _async_is_alive(self) -> bool:
        """Is the kernel process still running?"""
        if not self.owns_kernel:
            return True
        
        return True

    @property
    def is_remote(self): 
        return True
    
    @property
    def delegate_kernel_id(self):
        return self.kernel_instance["id"]
    
    @property
    def delegate_multi_kernel_manager(self):
        return self.remote_manager
    
    @property
    def has_kernel(self):
        return True

    def client(self, *args, **kwargs):
        return self.remote_manager
    
    async def cleanup_resources(self, *args, **kwargs):
        pass
    