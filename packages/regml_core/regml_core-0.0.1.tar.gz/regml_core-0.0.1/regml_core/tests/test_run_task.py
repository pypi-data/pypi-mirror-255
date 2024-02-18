from regml_core.lib.remote_host import RegMLHttpRemoteConnector, RegMLRemoteHost, RegMLRemoteHostConfigArgs
import asyncio

if __name__ == "__main__":
    async def main():
        connector = RegMLHttpRemoteConnector("https://regml.regscale.io/regml/api/examples/generic")
        remote_host = RegMLRemoteHost(connector, RegMLRemoteHostConfigArgs())
        spec = await remote_host.run_task({
            "typeName": "RegMLRunTaskThunk",
            "taskName": "LLMChat",
            "taskVersion": "0.0.0",
            "taskArgs": {
                "base": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Print only the exact words in the quotes. Do not include the quotes: \"HELLO WORLD\""
                        }
                    ]
                },
                "provider": {}
            }
        })

        print(spec)
    
    asyncio.run(main())