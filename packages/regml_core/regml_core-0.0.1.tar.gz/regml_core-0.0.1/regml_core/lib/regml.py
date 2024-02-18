
from dataclasses import dataclass

@dataclass
class RegMLConfigArgs:
    remote_hosts: Optional[TRemoteHosts] = None
    # To get us up and running, we've opted for a minimal set of required arguments.
    # The other arguments here should be added at a later date.
    # security_policies: RegMLCoreDataSecurityPolicy
    # providers: Optional[TLocalProviders] = None
    # callbacks: Optional[RegMLCallbackHandler] = None
    # custom_instance_id: Optional[str] = None


class RegML(object):
    def __init__(self, **kwargs):
        self._regml = _regml.RegML(**kwargs)

    def run(self, **kwargs):
        return self._regml.run(**kwargs)
    

