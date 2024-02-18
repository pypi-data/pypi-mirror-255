import aiohttp
from typing import Dict
from .remote_connector import RegMLRemoteConnector
from typing import Callable
import asyncio

class RegMLHttpRemoteConnector(RegMLRemoteConnector[str, Dict, Dict]):
    def __init__(self, url: str, headers: Dict[str, str] = None, fetch: Callable = None):
        self.url = url
        self.headers = headers if headers is not None else {}
        self.fetch = fetch  # This can be used to inject a custom fetch method, if required.

    async def send(self, message: Dict) -> Dict:
        headers = {'Content-Type': 'application/json', **self.headers}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=message, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(response)
                    # Handle non-200 responses appropriately.
                    return {'success': False, 'errors': [f'Response status {response.status}']}
                

if __name__ == "__main__":
    async def main():
        connector = RegMLHttpRemoteConnector("https://regml.regscale.io/regml/api/examples/generic")
        message = {"typeName":"getHostSpec","body":{"filters":{}}}
        response = await connector.send(message)
        print(response)
    
    asyncio.run(main())

