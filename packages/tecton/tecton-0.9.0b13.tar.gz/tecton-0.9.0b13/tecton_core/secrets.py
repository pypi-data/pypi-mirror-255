from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Mapping
from typing import NamedTuple

from tecton_proto.common.secret_pb2 import SecretReference


class SecretCacheKey(NamedTuple):
    scope: str
    key: str


class SecretContext:
    """SecretContext is passed as an argument to UDF functions to provide secret values."""

    def __init__(self, secret_dict: Mapping[SecretCacheKey, str]) -> None:
        self._secret_dict: Mapping[SecretCacheKey, str] = secret_dict.copy()

    def get(self, scope: str, key: str) -> str:
        """Get secret value by secret scope and key."""
        lookup_key = SecretCacheKey(scope, key)
        if lookup_key not in self._secret_dict:
            msg = "Secret not found for scope: {scope}, key: {key}"
            raise KeyError(msg)
        return self._secret_dict[lookup_key]


class SecretResolver(ABC):
    """Abstract Secret Resolver to resolve secret references to their values.

    Abstract class is used to allow for different implementations of secret resolution, for example,
    fetching secrets from MDS during materialization, or fetching secrets from a environment in local development.
    """

    @abstractmethod
    def resolve(self, secrets: List[SecretReference]) -> SecretContext:
        raise NotImplementedError
