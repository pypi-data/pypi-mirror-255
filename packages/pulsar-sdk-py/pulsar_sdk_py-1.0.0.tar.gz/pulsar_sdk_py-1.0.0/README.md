![alt text](https://i.imgur.com/jVdp3yy.png)

<div id="top"></div>

This library serves as a way to interact with Pulsar's Third Party APIs.
Provided you have an API Key, getting started is very easy.

E.g. on how to fetch balances from a wallet:

```python
import asyncio
from pulsar_sdk_py import PulsarSDK
from pulsar_sdk_py.enums import ChainKeys

API_KEY = "API_KEY_HERE"
sdk = PulsarSDK(API_KEY)


async def fetch_balances(wallet_address: str, chain: ChainKeys):
    responses_list = []
    async for wallet_balance in sdk.balances.get_wallet_balances(
            wallet_addr=wallet_address,
            chain=chain
    ):
        responses_list.append(wallet_balance)
    return responses_list


res = asyncio.get_event_loop().run_until_complete(
    fetch_balances("0x77984dc88aab3d9c843256d7aabdc82540c94f69", ChainKeys.ETHEREUM)
)
print(res)
```

Which will fetch you all the wallet balances for your wallet, provided the Chain is active in our environment.

For more information, check out our [documentation](http://pulsar.readme.io/).
