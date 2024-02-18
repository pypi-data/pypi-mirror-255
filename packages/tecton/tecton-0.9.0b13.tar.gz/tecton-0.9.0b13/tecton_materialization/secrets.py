from types import MappingProxyType
from typing import Dict
from typing import List

import requests

from tecton_core.secrets import SecretCacheKey
from tecton_core.secrets import SecretContext
from tecton_core.secrets import SecretReference
from tecton_core.secrets import SecretResolver


class MDSSecretResolver(SecretResolver):
    """Implementation of SecretsResolver that fetches secrets from the Tecton Secret Service and caches in-memory.

    Example:
        secret_resolver = SecretResolver(secrets_api_service_url="https://example.tecton.ai", api_key="my_api_key")
        resolved_secrets = secret_resolver.resolve([SecretReference(scope="prod", key="db_password")])
        db_password = resolved_secrets.get("prod", "db_password")
    """

    def __init__(self, secrets_api_service_url: str, api_key: str) -> None:
        if not api_key:
            msg = "Tecton secrets access API key not found."
            raise RuntimeError(msg)
        # TODO: Switch to use PureHTTPStub, which allow service proto annotation once TEC-18444 is resolved.
        self.api_url = f"{secrets_api_service_url}/v1/secrets-service/get-secret-value"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Tecton-Key {api_key}"})
        self.secret_cache: Dict[SecretCacheKey, str] = {}

    def resolve(self, secrets: List[SecretReference]) -> SecretContext:
        resolved_secrets_dict = {}
        for secret in secrets:
            cache_key = SecretCacheKey(secret.scope, secret.key)
            if cache_key not in self.secret_cache:
                self.secret_cache[cache_key] = self._fetch_secret(secret.scope, secret.key)
            resolved_secrets_dict[cache_key] = self.secret_cache[cache_key]
        return SecretContext(MappingProxyType(resolved_secrets_dict))

    def _fetch_secret(self, scope: str, key: str) -> str:
        """Fetch the secret value from the Secret Manager Service via HTTP."""
        payload = {"scope": scope, "key": key}
        response = self.session.post(self.api_url, json=payload, verify=True)

        response.raise_for_status()
        response_json = response.json()
        if "secret_value" in response_json and "value" in response_json["secret_value"]:
            return response_json["secret_value"]["value"]
        else:
            msg = f"Secret value not found when resolving secret for scope: {scope}, key: {key}"
            raise KeyError(msg)
