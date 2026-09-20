from typing import Protocol, runtime_checkable

from lattence.governance import ResolvedIdentity, Role


@runtime_checkable
class SSOProvider(Protocol):
    def resolve(self, bearer_token: str) -> ResolvedIdentity | None:
        """Resolve an external identity token to a Lattence caller and roles.

        Returns None when the token is not one this provider recognizes,
        so `require_access` can fall through to RBAC and the legacy token.
        An implementation for a real identity provider validates the token
        (for example, an OIDC access or ID token signature and issuer)
        before returning an identity; this protocol takes no position on
        how that validation happens.
        """
        ...


class MockSSOProvider:
    """A reference SSOProvider for tests and local development.

    Recognizes tokens of the form ``mock-sso:<caller_id>:<role,role,...>``
    and resolves them without contacting any external service. A real
    OIDC provider implementation exchanges the bearer token for verified
    claims instead of parsing them out of the token string itself.
    """

    _PREFIX = "mock-sso:"

    def resolve(self, bearer_token: str) -> ResolvedIdentity | None:
        if not bearer_token.startswith(self._PREFIX):
            return None
        remainder = bearer_token.removeprefix(self._PREFIX)
        caller_id, _, roles_csv = remainder.partition(":")
        if not caller_id:
            return None
        roles = frozenset(Role(value) for value in roles_csv.split(",") if value)
        return ResolvedIdentity(caller_id=caller_id, roles=roles)


_active_provider: SSOProvider | None = None


def set_sso_provider(provider: SSOProvider | None) -> None:
    global _active_provider
    _active_provider = provider


def active_sso_provider() -> SSOProvider | None:
    return _active_provider
