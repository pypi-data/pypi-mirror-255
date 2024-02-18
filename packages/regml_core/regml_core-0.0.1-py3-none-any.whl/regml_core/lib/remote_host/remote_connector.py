from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Union

TName = TypeVar('TName', bound=str)
TRequest = TypeVar('TRequest', bound=Dict[str, Any])
TResponse = TypeVar('TResponse', bound=Union[Dict[str, Any], None])

class RegMLRemoteConnector(ABC, Generic[TName, TRequest, TResponse]):
    @abstractmethod
    async def send(self, message: TRequest) -> TResponse:
        pass