from dataclasses import dataclass, field
from typing import Optional, Callable, Dict
from typing import Any, List
from .remote_connector import RegMLRemoteConnector
from .remote_host_error import RemoteHostError
import asyncio

@dataclass
class RegMLRemoteHostConfigArgs:
    host_spec_caching: Optional[Dict[str, int]] = field(default_factory=lambda: {'cacheDurationMs': 30 * 1000})
    callbacks: Optional[Dict[str, Callable]] = None



@dataclass
class RegMLHostSpec:
    regml_instance_id: str
    remote_host_id: Optional[str] = None
    metadata: Any = field(default_factory=dict)
    provider_specs: List[Any] = field(default_factory=list)  # Specify more detailed type if available
    env_spec: Any = field(default_factory=dict)
    remote_host_specs: List[Any] = field(default_factory=list)  # Specify more detailed type if available


from abc import ABC, abstractmethod

class RegMLRemoteHost(ABC):
    def __init__(self, connector: RegMLRemoteConnector, config: RegMLRemoteHostConfigArgs):
        self.connector = connector
        self.config = config or {}
        self._instance_id = "unique_identifier_here"  # This should be generated or provided
        self._get_spec_cache = None
        self._get_spec_lock = asyncio.Lock()

    @property
    def instance_id(self):
        return self._instance_id

    @abstractmethod
    async def get_spec(self):
        pass

    async def get_spec(self):
        async with self._get_spec_lock:
            if self._get_spec_cache:
                return self._get_spec_cache

            # Placeholder for callback logic, if any
            # self.config.get('callbacks', {}).get('onGetSpecRequested', lambda: None)()

            # Example request to the connector
            response = await self.connector.send({
                "typeName": "getHostSpec",
                "body": {}
            })

            if not response.get('success'):
                raise Exception("Failed to get host spec")

            self._get_spec_cache = response['body']

            # Placeholder for callback logic, if any
            # self.config.get('callbacks', {}).get('onGetSpecReceived', lambda spec: None)(self._get_spec_cache)

            # Throttle requests - reset cache after a delay
            cache_duration = self.config.host_spec_caching.get('cacheDurationMs', 30 * 1000) / 1000
            asyncio.create_task(self._reset_cache_after_delay(cache_duration))

            return self._get_spec_cache

    async def _reset_cache_after_delay(self, delay: float):
        await asyncio.sleep(delay)
        async with self._get_spec_lock:
            self._get_spec_cache = None

    async def run_task(self, solved_task_thunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a task to the remote host for execution.

        Args:
            solved_task_thunk: The task thunk containing all necessary information for the remote host to execute the task.

        Returns:
            The result of the task execution as returned by the remote host.
        """
        try:
            response = await self.connector.send({
                "typeName": "runTask",
                "body": {
                    "taskThunk": solved_task_thunk,
                }
            })

            print(response)

            if response.get('success'):
                return response['body']['taskResponse']
            else:
                raise RemoteHostError(
                    "Failed to run task on remote host.",
                    self._instance_id,
                    response.get('errors', [])
                )
        except Exception as e:
            # Log or handle the exception as needed
            raise RemoteHostError(f"Exception occurred while running task: '{str(e)}'", self._instance_id)