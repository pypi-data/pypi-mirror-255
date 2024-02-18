"""
This file loads and provide an object `config` to access all secrets, configs, and chain info
"""

import itertools
import os
from dataclasses import dataclass, field, fields
from typing import List, Optional, Union

import yaml

MISSING_CONFIG_MSG = "Configuration or environment variable {x} is not set or unknown"

ENV = None
try:
    ENV = os.environ['ENV']
except KeyError:
    raise ValueError(MISSING_CONFIG_MSG.format(x='ENV'))


class ConfigObj:
    """Raise an error if a config is not set."""

    def __getattr__(self, name):
        raise AttributeError(MISSING_CONFIG_MSG.format(x=name))

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if value == "" or value is None:
            raise AttributeError  # induces a call to __getattr__
        return value

    def __iter__(self):
        """Allow iterating over set values"""
        for subfield in fields(self):
            try:
                value = getattr(self, subfield.name)
            except AttributeError:
                continue
            yield value


class ConfigDict(dict):
    def __getitem__(self, key):
        """Raise an error if an unset key is indexed."""
        try:
            value = super().__getitem__(key)
            if value == "" or value is None:
                raise KeyError
            return value
        except KeyError:
            raise KeyError(MISSING_CONFIG_MSG.format(x=key))


# Use ConfigDict in the yaml parser
class Loader(yaml.FullLoader):
    def construct_yaml_map(self, node):
        data = ConfigDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


Loader.add_constructor('tag:yaml.org,2002:map', Loader.construct_yaml_map)


@dataclass(repr=False)
class ChainConfig(ConfigObj):
    name: str = ""
    id: str = ""
    # Optional. For looking up prices on coingecko if it differs from name
    coingecko_name: str = ""
    denom: str = ""
    denom_decimals: int = 6
    inflation_frequency_hours: int = -1
    ticker: str = ""
    stride_token_hash: str = ""
    api_endpoint: str = ""
    rpc_endpoint: str = ""
    library_api: str = ""
    library_rpc: str = ""


@dataclass(repr=False)
class HostZoneChainConfig(ConfigObj):
    cosmoshub: ChainConfig = field(default_factory=ChainConfig)
    osmosis: ChainConfig = field(default_factory=ChainConfig)
    evmos: ChainConfig = field(default_factory=ChainConfig)
    injective: ChainConfig = field(default_factory=ChainConfig)
    juno: ChainConfig = field(default_factory=ChainConfig)
    stargaze: ChainConfig = field(default_factory=ChainConfig)
    terra: ChainConfig = field(default_factory=ChainConfig)
    umee: ChainConfig = field(default_factory=ChainConfig)
    comdex: ChainConfig = field(default_factory=ChainConfig)
    sommelier: ChainConfig = field(default_factory=ChainConfig)
    dydx: ChainConfig = field(default_factory=ChainConfig)


@dataclass(repr=False)
class AppConfig(ConfigObj):
    neutron: ChainConfig = field(default_factory=ChainConfig)
    kava: ChainConfig = field(default_factory=ChainConfig)
    iris: ChainConfig = field(default_factory=ChainConfig)
    akash: ChainConfig = field(default_factory=ChainConfig)
    sentinel: ChainConfig = field(default_factory=ChainConfig)
    persistence: ChainConfig = field(default_factory=ChainConfig)
    cryptoorg: ChainConfig = field(default_factory=ChainConfig)
    kichain: ChainConfig = field(default_factory=ChainConfig)
    bitcanna: ChainConfig = field(default_factory=ChainConfig)
    regen: ChainConfig = field(default_factory=ChainConfig)
    gravity: ChainConfig = field(default_factory=ChainConfig)
    desmos: ChainConfig = field(default_factory=ChainConfig)
    chihuahua: ChainConfig = field(default_factory=ChainConfig)
    secret: ChainConfig = field(default_factory=ChainConfig)
    axelar: ChainConfig = field(default_factory=ChainConfig)
    crescent: ChainConfig = field(default_factory=ChainConfig)
    mantle: ChainConfig = field(default_factory=ChainConfig)
    mars: ChainConfig = field(default_factory=ChainConfig)
    canto: ChainConfig = field(default_factory=ChainConfig)
    agoric: ChainConfig = field(default_factory=ChainConfig)
    celestia: ChainConfig = field(default_factory=ChainConfig)


@dataclass(repr=False)
class Config(ConfigObj):
    ENV: str
    timezone: str = "US/Eastern"

    # Twilio
    TWILIO_ALERTS_NUMBER: str = ""
    TWILIO_ACCOUNT_ID: str = ""
    TWILIO_API_TOKEN: str = ""
    PHONE_NUMBERS: ConfigDict = field(default_factory=ConfigDict)

    # Slack
    STRIDEBOT_API_TOKEN: str = ""

    # Gsheets - loads from str env var in PROD
    PUBLICSHEETS_AUTH: Union[str, ConfigDict] = field(default_factory=ConfigDict)

    # Coingecko
    COINGECKO_API_TOKEN: str = ""

    # Stride alerts
    alerts_playbook: str = ""
    slack_channels: ConfigDict = field(default_factory=ConfigDict)

    # Upstash
    UPSTASH_PUBLIC_PASSWORD: str = ""
    UPSTASH_STRIDE_FRONTEND_PASSWORD: str = ""
    UPSTASH_STRIDE_BACKEND_PASSWORD: str = ""

    # Stride internal secrets
    SLACK_BEARER_TOKEN: str = ""
    SLACK_SUCCESS_CHANNEL_ID: str = ""
    SLACK_INVARIANT_FAILURE_CHANNEL_ID: str = ""
    SLACK_PACKET_FAILURE_CHANNEL_ID: str = ""
    NUMIA_API_TOKEN: str = ""
    founders: List[str] = field(default_factory=lambda: ['riley', 'aidan', 'vishal'])

    # Chain configs
    stride: ChainConfig = field(default_factory=ChainConfig)
    host_zones: HostZoneChainConfig = field(default_factory=HostZoneChainConfig)
    app_chains: AppConfig = field(default_factory=AppConfig)

    def _create_mappings(self) -> None:
        """
        Create a reverse map from attributes to ChainConfig if id, ticker, and denom are set.
        """
        name_to_zone = ConfigDict()
        id_to_zone = ConfigDict()
        ticker_to_zone = ConfigDict()
        denom_to_zone = ConfigDict()
        stride_token_hash_to_zone = ConfigDict()

        # Map host zones
        for chain_info in itertools.chain(self.host_zones, self.app_chains):
            name_to_zone[chain_info.name] = chain_info

            try:
                id_to_zone[chain_info.id] = chain_info
            except AttributeError:
                pass

            try:
                ticker_to_zone[chain_info.ticker] = chain_info
                ticker_to_zone[chain_info.ticker.upper()] = chain_info
                ticker_to_zone[chain_info.ticker.lower()] = chain_info
                ticker_to_zone[chain_info.ticker.denom[1].upper()] = chain_info
            except AttributeError:
                pass

            try:
                denom_to_zone[chain_info.denom] = chain_info
            except AttributeError:
                pass

            try:
                stride_token_hash_to_zone[chain_info.stride_token_hash] = chain_info
            except AttributeError:
                pass

        self._name_to_zone = name_to_zone
        self._id_to_zone = id_to_zone
        self._ticker_to_zone = ticker_to_zone
        self._denom_to_zone = denom_to_zone
        self._stride_token_hash = stride_token_hash_to_zone

    def __post_init__(self):
        self._create_mappings()

    def get_chain(  # type: ignore[return]
        self,
        name: Optional[str] = None,
        id: Optional[str] = None,
        ticker: Optional[str] = None,
        denom: Optional[str] = None,
        stride_token_hash: Optional[str] = None,
    ) -> ChainConfig:
        """
        Fetch info about a host zone by name, id, ticker, denom, or token hash.

        Raises
            KeyError if a valid chain doesn't exist
        """
        if sum(map(bool, [name, id, ticker, denom, stride_token_hash])) != 1:
            raise ValueError("Exactly one of name, id, ticker, denom, or token hash must be specified.")

        if (
            name == self.stride.name
            or id == self.stride.id
            or ticker == self.stride.ticker
            or denom == self.stride.denom
        ):
            return self.stride
        elif name:
            return self._name_to_zone[name]
        elif id:
            return self._id_to_zone[id]
        elif ticker:
            return self._ticker_to_zone[ticker]
        elif denom:
            return self._denom_to_zone[denom]
        elif stride_token_hash:
            return self._stride_token_hash[stride_token_hash]


# Load chain config
def _load() -> Config:
    """
    Load config dataclasses based on environment
    """
    STRIDEUTILS_CONFIG_PATH = os.environ.get('STRIDEUTILS_CONFIG_PATH', 'config/config.yaml')
    if not os.path.exists(STRIDEUTILS_CONFIG_PATH):
        raise ValueError(
            'Shell var STRIDEUTILS_CONFIG_PATH is missing or the file does not exist.'
            'The default file and location is config/config.yaml in the current working directory'
        )

    with open(STRIDEUTILS_CONFIG_PATH, 'r') as f:
        raw_config = yaml.load(f, Loader)
        stride_chain_config = ChainConfig(**raw_config.get('stride'))
        host_zone_config = HostZoneChainConfig(
            **{name: ChainConfig(**info) for name, info in raw_config.get('host_zones').items()}
        )
        app_chain_config = AppConfig(
            **{name: ChainConfig(**info) for name, info in raw_config.get('app_chains').items()}
        )
    chain_configs = {
        'stride': stride_chain_config,
        'host_zones': host_zone_config,
        'app_chains': app_chain_config,
    }

    # Load secrets
    if ENV == 'DEV':
        if not (STRIDEUTILS_SECRETS_PATH := os.environ.get('STRIDEUTILS_SECRETS_PATH')):
            raise ValueError(MISSING_CONFIG_MSG.format(x='STRIDEUTILS_SECRETS_PATH'))
        with open(STRIDEUTILS_SECRETS_PATH, 'r') as f:
            raw_secrets = yaml.load(f, Loader)
            raw_secrets.update({'ENV': ENV})
    elif ENV == 'PROD':
        raw_secrets = {
            secret.name: os.environ.get(secret.name) for secret in fields(Config) if os.environ.get(secret.name)
        }

    # Load vanilla configs
    raw_secrets.update(raw_config)
    # Overwrite prepped ChainConfigs
    raw_secrets.update(chain_configs)
    config = Config(**raw_secrets)
    return config


config: Config = _load()
