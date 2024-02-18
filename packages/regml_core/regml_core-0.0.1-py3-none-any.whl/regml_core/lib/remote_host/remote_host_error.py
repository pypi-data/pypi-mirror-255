class RemoteHostError(Exception):
    def __init__(self, message: str, remote_host_id: str, errors=None):
        super().__init__(message)
        self.remote_host_id = remote_host_id
        self.errors = errors if errors is not None else []
        self.name = 'RemoteHostError'