from typing import TypedDict, Literal


# Data Interface
class Data(TypedDict):
    address: str
    chain: str


# WalletBalancesData Interface
class WalletBalancesData(Data, total=False):
    ignore_cache: bool
    hide_nfts: set[str]
    hide_tokens: set[str]
    hide_integrations: set[str]
    fetch_nfts: bool
    fetch_tokens: bool
    fetch_integrations: bool


# TimeseriesData Interface
class TimeseriesData(Data):
    tier: str


# Command Interface
class WalletBalancesCommand(TypedDict):
    key: Literal["WALLET_BALANCES"]
    data: WalletBalancesData


class TimeseriesCommand(TypedDict):
    key: Literal["GET_WALLET_TIMESERIES"]
    data: TimeseriesData


# Message Interface
class Message(TypedDict):
    method: str
    request_id: str


# Specific Message Types
class BalancesMessage(Message):
    command: WalletBalancesCommand


class TimeseriesMessage(Message):
    command: TimeseriesCommand
