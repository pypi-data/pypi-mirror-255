from pulsar_sdk_py.rest.base import PulsarRestClientAPI
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.dataclasses.schemas import ResolvedName, ResolvedAddress


class NameServiceRestClient(PulsarRestClientAPI):
    def resolve_name(self, name: str) -> ResolvedName:
        response = self._request(path="/name-service/resolve-name", request_type="GET", name=name)
        return serialize_to_dataclass(response, ResolvedName)

    def resolve_address(self, address: str) -> ResolvedAddress:
        response = self._request(path="/name-service/resolve-address", request_type="GET", address=address)
        return serialize_to_dataclass(response, ResolvedAddress)
