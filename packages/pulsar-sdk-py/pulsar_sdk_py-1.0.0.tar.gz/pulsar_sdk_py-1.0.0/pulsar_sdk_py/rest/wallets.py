from pulsar_sdk_py.enums import TierKeys, ChainKeys
from pulsar_sdk_py.rest.base import PulsarRestClientAPI
from pulsar_sdk_py.dataclasses.schemas import TimeseriesWithStats
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass


class WalletRestClient(PulsarRestClientAPI):
    def get_wallet_timeseries(
        self, address: str, chain: ChainKeys, tier: TierKeys = TierKeys.ONE_DAY
    ) -> TimeseriesWithStats:
        response = self._request(
            path="/wallet/{address}/timeseries", request_type="GET", address=address, chain=chain, tier=tier
        )
        return serialize_to_dataclass(response, TimeseriesWithStats)
