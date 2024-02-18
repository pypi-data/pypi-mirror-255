from pulsar_sdk_py.rest.base import PulsarRestClientAPI
from pulsar_sdk_py.helpers import filter_non_empty_params
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.enums import ChainKeys, NFTItemSort, NFTCollectionSort
from pulsar_sdk_py.dataclasses.schemas import (
    NFTItem,
    NFTCollection,
    NFTTraitsFilter,
    PaginatedNFTItems,
    PaginatedNFTCollections,
)


class NFTRestClient(PulsarRestClientAPI):
    def list_collection_nfts(
        self,
        collection_id: str,
        search_string: str | None = None,
        rarity_score: str | None = None,
        rank_minimum: int | None = None,
        rank_maximum: int | None = None,
        traits: NFTTraitsFilter | None = None,
        sort_by: NFTItemSort | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedNFTItems:
        params_filtered = filter_non_empty_params(
            collection_id=collection_id,
            search_string=search_string,
            rarity_score=rarity_score,
            rank_minimum=rank_minimum,
            rank_maximum=rank_maximum,
            sort_by=sort_by,
            offset=offset,
            limit=limit,
        )

        traits_dict = {"traits": [] if traits is None else traits.traits}

        response = self._request(
            path="/nfts/collections/{collection_id}/nfts",
            request_type="POST",
            request_body=traits_dict,
            **params_filtered,
        )
        return serialize_to_dataclass(response, PaginatedNFTItems)

    def fetch_collection(self, collection_id: str) -> NFTCollection:
        response = self._request(
            path="/nfts/collections/{collection_id}", request_type="GET", collection_id=collection_id
        )
        return serialize_to_dataclass(response, NFTCollection)

    def fetch_collection_by_address(self, collection_address: str, chain: ChainKeys) -> NFTCollection:
        response = self._request(
            path="/nfts/collections/{chain}/{collection_address}",
            request_type="GET",
            collection_address=collection_address,
            chain=chain,
        )
        return serialize_to_dataclass(response, NFTCollection)

    def fetch_nft(self, collection_id: str, token_id: str) -> NFTItem:
        response = self._request(
            path="/nfts/collections/{collection_id}/nfts/{token_id}",
            request_type="GET",
            collection_id=collection_id,
            token_id=token_id,
        )
        return serialize_to_dataclass(response, NFTItem)

    def fetch_nft_by_address(self, collection_address: str, chain: ChainKeys, token_id: str) -> NFTItem:
        response = self._request(
            path="/nfts/collections/{chain}/{collection_address}/nfts",
            request_type="GET",
            collection_address=collection_address,
            chain=chain,
            token_id=token_id,
        )
        return serialize_to_dataclass(response, NFTItem)

    def list_nfts(
        self,
        name: str | None = None,
        chains: list[ChainKeys] | None = None,
        sort_by: NFTCollectionSort | None = None,
        offset: int = 0,
        limit: int = 10,
        floor_minimum: float | None = None,
        floor_maximum: float | None = None,
        is_fully_index: bool = True,
    ) -> PaginatedNFTCollections:
        params_filtered = filter_non_empty_params(
            name=name,
            chains=chains,
            sort_by=sort_by,
            offset=offset,
            limit=limit,
            floor_minimum=floor_minimum,
            floor_maximum=floor_maximum,
            is_fully_index=is_fully_index,
        )
        response = self._request(path="/nfts", request_type="GET", **params_filtered)
        return serialize_to_dataclass(response, PaginatedNFTCollections)
