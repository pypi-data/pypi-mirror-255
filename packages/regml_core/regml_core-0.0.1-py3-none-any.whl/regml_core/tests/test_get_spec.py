from regml_core.lib.remote_host import RegMLHttpRemoteConnector, RegMLRemoteHost, RegMLRemoteHostConfigArgs
import asyncio

if __name__ == "__main__":
    async def main():
        connector = RegMLHttpRemoteConnector("https://regml.regscale.io/regml/api/examples/generic")
        remote_host = RegMLRemoteHost(connector, RegMLRemoteHostConfigArgs())
        spec = await remote_host.get_spec()
        print(spec)
    
    asyncio.run(main())