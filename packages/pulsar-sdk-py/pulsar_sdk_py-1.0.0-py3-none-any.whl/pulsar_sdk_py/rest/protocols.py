from pulsar_sdk_py.rest.base import PulsarRestClientAPI
from pulsar_sdk_py.helpers import filter_non_empty_params
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.enums import TierKeys, ChainKeys, ProtocolSort
from pulsar_sdk_py.dataclasses.schemas import ProtocolData, ProtocolTimeseries, PaginatedProtocols


class ProtocolRestClient(PulsarRestClientAPI):
    def list_protocols(self, chain: ChainKeys | None = None) -> list[ProtocolData]:
        params_filtered = filter_non_empty_params(chain=chain)
        response = self._request(path="/protocols/all-protocols", request_type="GET", **params_filtered)
        return [serialize_to_dataclass(protocol, ProtocolData) for protocol in response]

    def get_number_protocols(self) -> int:
        return self._request("/protocols/total-protocols", request_type="GET")

    def get_filtered_protocols(
        self,
        name: str | None = None,
        chains: list[ChainKeys] | None = None,
        tvl: str | None = None,
        sort_by: ProtocolSort | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedProtocols:
        params_filtered = filter_non_empty_params(
            name=name, chains=chains, tvl=tvl, sort_by=sort_by, offset=offset, limit=limit
        )
        response = self._request(path="/protocols", request_type="GET", **params_filtered)
        return serialize_to_dataclass(response, PaginatedProtocols)

    def get_protocol_timeseries(self, protocol_key: str, tier_name: TierKeys) -> ProtocolTimeseries:
        response = self._request(
            path="/protocols/{protocol_key}/timeseries",
            request_type="GET",
            protocol_key=protocol_key,
            tier_name=tier_name,
        )
        return serialize_to_dataclass(response, ProtocolTimeseries)
