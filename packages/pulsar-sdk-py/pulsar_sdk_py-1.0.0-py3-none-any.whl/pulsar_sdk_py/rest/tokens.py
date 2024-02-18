from pulsar_sdk_py.rest.base import PulsarRestClientAPI
from pulsar_sdk_py.helpers import filter_non_empty_params
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.enums import TierKeys, ChainKeys, TokenSort, TokenType
from pulsar_sdk_py.dataclasses.schemas import ExtendedToken, TokenPriceTimeseries, PaginatedTokens


class TokenRestClient(PulsarRestClientAPI):
    def get_token_info_by_id(self, token_id: str) -> ExtendedToken:
        response = self._request(path="/token/{token_id}", request_type="GET", token_id=token_id)
        return serialize_to_dataclass(response, ExtendedToken)

    def get_token_info_by_address_and_chain(
        self, token_type: TokenType, address: str, chain: ChainKeys
    ) -> ExtendedToken:
        """
        Deprecated: Use `get_token_info` instead.
        """
        return self.get_token_info(token_type, address, chain)

    def get_token_info(self, token_type: TokenType, address: str, chain: ChainKeys) -> ExtendedToken:
        response = self._request(
            path="/token/{token_type}/{address}",
            request_type="GET",
            token_type=token_type,
            address=address,
            chain=chain,
        )
        return serialize_to_dataclass(response, ExtendedToken)

    def list_tokens(
        self,
        text: str | None = None,
        chains: list[ChainKeys] | None = None,
        minimum_liquidity: int = 0,
        sort_by: TokenSort | None = None,
        whitelisted_only: bool = False,
        remove_blacklisted: bool = False,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedTokens:
        params_filtered = filter_non_empty_params(
            text=text,
            chains=chains,
            sort_by=sort_by,
            offset=offset,
            limit=limit,
            minimum_liquidity=minimum_liquidity,
            whitelisted_only=whitelisted_only,
            remove_blacklisted=remove_blacklisted,
        )
        response = self._request(path="/tokens", request_type="GET", **params_filtered)
        return serialize_to_dataclass(response, PaginatedTokens)

    def get_token_timeseries(self, token_id: str, tier_name: TierKeys) -> TokenPriceTimeseries:
        response = self._request(
            path="/tokens/{token_id}/timeseries", request_type="GET", token_id=token_id, tier_name=tier_name
        )
        return serialize_to_dataclass(response, TokenPriceTimeseries)
