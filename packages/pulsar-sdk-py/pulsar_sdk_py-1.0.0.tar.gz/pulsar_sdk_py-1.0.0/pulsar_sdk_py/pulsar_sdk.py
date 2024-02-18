from functools import cached_property

from pulsar_sdk_py.websocket import WalletBalancesClient, WebSocketClient
from pulsar_sdk_py.rest import (
    NFTRestClient,
    TokenRestClient,
    WalletRestClient,
    ProtocolRestClient,
    NameServiceRestClient,
)


class PulsarSDK:
    """
    A client for interacting with the Pulsar Third Party API.

    This class provides a high-level interface for interacting with the API, including the ability to
    retrieve data about tokens, domain names, NFTs, protocols, and wallet balances. The class serves typified ways to
    interact with the endpoints, through websockets or REST.

    ### Parameters:
        - `api_key`(str): The API key to use for the API. (required)
        - `base_url`(str): The base URL to use for the API. (optional)
        - `use_ssl`(bool): Whether to use SSL for the API. (optional)
    """

    nfts: NFTRestClient
    tokens: TokenRestClient
    wallets: WalletRestClient
    protocols: ProtocolRestClient
    balances: WalletBalancesClient
    name_service: NameServiceRestClient

    @cached_property
    def REST_API_URL(self) -> str:
        return f"{self._PROTOCOL}://{self._BASE_URL}/v1/thirdparty"

    @cached_property
    def WS_API_URL(self) -> str:
        return f"{self._WS_PROTOCOL}://{self._BASE_URL}/v1/thirdparty/ws"

    def __init__(self, api_key: str, base_url: str | None = None, use_ssl: bool = True):
        self._BASE_URL = base_url or "alpha-api.pulsar.finance"

        if not api_key or not isinstance(api_key, str):
            raise ValueError("Please pass a correct API key to PulsarSDK.\neg: PulsarSDK('key_here')")

        self._PROTOCOL = "https" if use_ssl else "http"
        self._WS_PROTOCOL = "wss" if use_ssl else "ws"
        headers = {"Authorization": f"Bearer {api_key}"}

        # Rest clients
        self.tokens = TokenRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.name_service = NameServiceRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.nfts = NFTRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.protocols = ProtocolRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.wallets = WalletRestClient(rest_api_url=self.REST_API_URL, headers=headers)

        # Websocket clients
        self.balances = WalletBalancesClient(ws_client=WebSocketClient(ws_url=self.WS_API_URL, api_key=api_key))
