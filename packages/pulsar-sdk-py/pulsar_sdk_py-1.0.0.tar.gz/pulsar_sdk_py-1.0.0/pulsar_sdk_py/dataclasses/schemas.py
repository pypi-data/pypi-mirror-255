from dataclasses import dataclass, field

from pulsar_sdk_py.enums import (
    DebtType,
    TierKeys,
    OrderType,
    ChainKeys,
    TokenType,
    OptionType,
    AnnualReturnType,
    TimeseriesEventKey,
)


@dataclass
class TokenChain:
    type: TokenType
    value: str


@dataclass
class TokenChainWithDecimals(TokenChain):
    decimals: int | None


@dataclass
class TokenChainInfo:
    chain: ChainKeys
    id: TokenChain
    decimals: int | None


@dataclass
class BaseToken:
    name: str
    denom: str
    id: str
    display_id: str
    image: str | None = None
    latest_price: str | None = None
    price_24h_change: str | None = None
    chain_properties: TokenChainInfo | None = None


@dataclass
class BaseWallet:
    address: str
    chain: str


@dataclass
class NFTCollectionMarketplace:
    indexer_id: str
    slug_id: str | None = None
    url: str | None = None
    marketplace_id: str | None = None


@dataclass
class NFTCollectionStats:
    price_timeseries: dict[str, str | None]


@dataclass
class NFTCollection:
    id: str
    address: str | None
    chain: str
    marketplaces: list[NFTCollectionMarketplace]
    number_of_assets: int | None
    number_of_owners: int | None
    available_traits: list[str] | None
    token: BaseToken | None
    last_24h_change: str | None = None
    last_24h_change_percentage: str | None = None
    name: str | None = None
    avatar: str | None = None
    banner: str | None = None
    description: str | None = None
    volume: str | None = None
    volume_usd: str | None = None
    average_price: str | None = None
    floor_price: str | None = None
    floor_price_usd: str | None = None
    market_cap: str | None = None
    market_cap_usd: str | None = None
    stats: NFTCollectionStats | None = None
    low_volume: bool = False
    unknown_volume: bool = False
    is_fully_index: bool = False


@dataclass
class NFTItem:
    name: str
    id: str
    token_id: str
    chain: str
    traits: dict[str, str] = field(default_factory=dict)
    traits_hash: str | None = None
    creator_address: str | None = None
    owner_address: str | None = None
    token: BaseToken | None = None
    wallet: BaseWallet | None = None
    collection: NFTCollection | None = None
    description: str | None = None
    avatar: str | None = None
    video_avatar: str | None = None
    price: str | None = None
    url: str | None = None
    urls: dict[str, str] = field(default_factory=dict)
    rarity_score: float | None = None
    rank: int | None = None


@dataclass
class WalletNFTError:
    indexer_id: str
    chain: ChainKeys


@dataclass
class WalletNFTs:
    items: list[NFTItem] | None
    errors: list[WalletNFTError]


@dataclass
class ResolvedName:
    main_name: str
    main_address: str
    service: str


@dataclass
class NFTTraitsFilter:
    traits: dict[str, list[str]]


@dataclass
class ResolvedAddress:
    main_name: str
    service: str


@dataclass
class PaginatedNFTItems:
    response: list[NFTItem]
    total: int


@dataclass
class TimeseriesEvent:
    event_key: TimeseriesEventKey
    event_data: dict


@dataclass
class Timeseries:
    wallet: BaseWallet
    tier: TierKeys
    timeseries: dict[str, float | None]
    events: dict[str, list[TimeseriesEvent]]


@dataclass
class NetworthStats:
    current_networth: float | None
    networth_difference: float | None
    percentage_difference: float | None


@dataclass
class TimeseriesWithStats(Timeseries):
    stats: NetworthStats


@dataclass
class RecipeData:
    key: str
    name: str
    chain: str


@dataclass
class ProtocolData:
    key: str
    name: str
    chains: list[str]
    image: str
    url: str
    recipes: dict[str, list[RecipeData]]
    integration_types: list[str]
    categories: list[str] | None
    tags: list[str]
    description: str | None
    twitter_url: str | None
    telegram_url: str | None


@dataclass
class ExtendedInformation:
    description: str | None = None
    categories: list[str] | None = None
    url_learn_more: str | None = None


@dataclass
class ExtendedToken(BaseToken):
    extended_information: ExtendedInformation | None = None
    addresses: dict[ChainKeys, TokenChainWithDecimals] = field(default_factory=dict)


@dataclass
class PaginatedNFTCollections:
    response: list[NFTCollection]
    total: int


@dataclass
class WalletToken:
    token: BaseToken
    wallet: BaseWallet
    usd_value: str | None
    balance: str


@dataclass
class SimpleToken:
    token_id: str
    name: str
    denom: str
    image: str | None = None


@dataclass
class TokenError:
    token: SimpleToken
    chain: ChainKeys


@dataclass
class WalletTokens:
    stats: list[WalletToken]
    errors: list[TokenError]


@dataclass
class ProtocolTimeseries:
    tier: str
    tvl_timeseries: dict[str, float | None]
    chain_tvl_timeseries: dict[str, dict[str, float | None]]


@dataclass
class TokenPriceTimeseries:
    tier: TierKeys
    timeseries: dict[str, float | None]


@dataclass
class TokenStats:
    market_cap: str
    total_liquidity: str | None = None
    price_oracles: list[str] | None = None
    last_24_hour_price: str | None = None
    last_24_hour_change: str | None = None
    last_24_hour_change_percentage: str | None = None
    last_7_day_price: str | None = None
    last_7_day_change: str | None = None
    last_7_day_change_percentage: str | None = None


@dataclass
class TokenAdvancedGlobalStats:
    price_timeseries: TokenPriceTimeseries | None = None
    market_cap_timeseries: dict[int, float | None] | None = None


@dataclass
class TokenWithStats:
    token: ExtendedToken
    stats: TokenStats


@dataclass
class APYStats:
    value: str | None = None
    type: str | None = None


@dataclass
class TvlStatsTokens:
    token: BaseToken
    amount: str
    usd_value: str | None


@dataclass
class TvlStats:
    tokens: list[TvlStatsTokens]
    usd_value: str | None


@dataclass
class BorrowStats:
    min_collateral_rate: str | None = None


@dataclass
class AirdropStats:
    latest_round: str | None = None


@dataclass
class ValidatorStats:
    name: str | None = None
    status: str | None = None
    address: str | None = None
    commission_percentage: str | None = None


@dataclass
class StakingStats:
    staking_type: str | None = None
    validator: ValidatorStats | None = None
    lp_token_name: str | None = None


@dataclass
class TokenApys:
    token: BaseToken
    apr: str


@dataclass
class MultiplierStats:
    total_apy: str | None = None
    base_apy: str | None = None
    rewards_apr: str | None = None
    reward_apr_per_token: list[TokenApys] | None = None
    sample_count: str | None = None
    variance_coefficient: str | None = None
    multiplier_deviation: str | None = None


@dataclass
class ImpermanentLossStats:
    percentage: str | None = None
    value: str | None = None
    time_ago: str | None = None


@dataclass
class RiskScoreStats:
    leverage_score: str | None = None
    impermanent_loss_score: str | None = None
    yield_outlook_score: str | None = None
    reward_token_score: str | None = None
    tvl_score: str | None = None
    global_score: str | None = None


@dataclass
class IntegrationStats:
    apy: APYStats | None = None
    tvl: TvlStats | None = None
    breakdown: list[BaseToken] = field(default_factory=list)
    nft_breakdown: list[NFTCollection] = field(default_factory=list)
    borrow_stats: BorrowStats | None = None
    airdrop_stats: AirdropStats | None = None
    staking_stats: StakingStats | None = None
    multiplier_stats: MultiplierStats | None = None
    impermanent_loss_stats: ImpermanentLossStats | None = None
    risk_score_stats: RiskScoreStats | None = None


@dataclass
class BaseIntegration:
    recipe_id: str
    integration_id: str
    chain: ChainKeys
    stats: IntegrationStats
    position_id: str | None = None
    name: str = ""
    platform: str = ""
    type: str = ""
    address: str | None = None


@dataclass
class IntegrationTokenStats:
    token: BaseToken
    wallet: BaseWallet
    usd_value: str | None
    balance: str
    balance_type: str
    unlock_timestamp: int | None = None


@dataclass
class IntegrationNFTStats:
    nft_collection: NFTCollection
    wallet: BaseWallet
    usd_value: str | None
    balance: str
    balance_type: str
    unlock_timestamp: int | None = None


@dataclass
class WalletIntegrationBorrowStats:
    interest_rate: str | None = None
    leverage_rate: str | None = None
    debt_type: DebtType | None = None
    min_collateral_rate: str | None = None
    interest_rate_type: AnnualReturnType | None = None
    health_rate: float | None = None


@dataclass
class WalletIntegrationAirdropStats:
    was_in_last_round: bool = False


@dataclass
class WalletIntegrationOptionStats:
    option_type: OptionType | None = None
    expiration_timestamp: int | None = None
    strike_price: str | None = None
    base_asset_name: str | None = None


@dataclass
class PartialToken:
    name: str
    denom: str


@dataclass
class WalletIntegrationOrderBookStats:
    base_token: BaseToken | PartialToken | None = None
    quote_token: BaseToken | PartialToken | None = None
    order_type: OrderType | None = None
    limit_price: str | None = None
    order_creation_timestamp: int | None = None


@dataclass
class WalletIntegrationApyStats(APYStats):
    pass


@dataclass
class WalletYieldStats:
    daily_base_rate: float | None = None
    daily_rewards_rate: float | None = None
    daily_yield: float | None = None


@dataclass
class WalletIntegrationStats:
    borrow_stats: WalletIntegrationBorrowStats | None = None
    airdrop_stats: WalletIntegrationAirdropStats | None = None
    option_stats: WalletIntegrationOptionStats | None = None
    order_book_stats: WalletIntegrationOrderBookStats | None = None
    apy: WalletIntegrationApyStats | None = None
    yield_stats: WalletYieldStats | None = None


@dataclass
class WalletIntegration:
    wallet: BaseWallet
    integration: BaseIntegration
    balances: list[IntegrationTokenStats] = field(default_factory=list)
    nft_balances: list[IntegrationNFTStats] = field(default_factory=list)
    wallet_stats: WalletIntegrationStats | None = None


@dataclass
class Recipe:
    recipe_id: str
    platform: str
    type: str


@dataclass
class RecipeError:
    recipe: Recipe
    chain: ChainKeys


@dataclass
class WalletIntegrations:
    stats: list[WalletIntegration]
    errors: list[RecipeError]


@dataclass
class PaginatedTokens:
    response: list[TokenWithStats]
    total: int


@dataclass
class ProtocolStats:
    total_tvl: str
    chain_tvl: dict[str, str]
    created_date: str | None


@dataclass
class ProtocolWithStats:
    protocol: ProtocolData
    stats: ProtocolStats


@dataclass
class PaginatedProtocols:
    response: list[ProtocolWithStats]
    total: int


@dataclass
class WalletRequestSettings:
    ignore_cache: bool = False
    ignore_empty_wallet_cache: bool = False
    hide_nfts: set[str] = field(default_factory=set)
    hide_tokens: set[str] = field(default_factory=set)
    hide_integrations: set[str] = field(default_factory=set)
    fetch_nfts: bool = True
    fetch_tokens: bool = True
    fetch_integrations: bool = True
