from typing import Optional
from plymouth_commons.config import Auth0Config, read_config
from asyncpg.pool import Pool

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


async def is_user_admin(auth0_sub: str, pool: Pool):
    async with pool.acquire() as conn:
        query = "select * from app_public.admins where user_id in (select id from app_public.users where auth0_sub = $1)"
        result = await conn.fetchrow(query, auth0_sub)
        return result is not None and len(result) > 0


class VerifyToken:
    """Token verification using PyJWT"""

    def __init__(self, auth0_config: Optional[Auth0Config] = None):
        if auth0_config is None:
            auth0_config = read_config(Auth0Config)

        self.config = auth0_config
        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{self.config.domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer()),
    ):
        if token is None:
            raise UnauthenticatedException

        # This gets the 'kid' from the passed token
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise UnauthorizedException(str(error))
        except jwt.exceptions.DecodeError as error:
            raise UnauthorizedException(str(error))

        try:
            payload = jwt.decode(
                token.credentials,
                signing_key,
                algorithms=["RS256"],
                audience=f"https://{self.config.domain}/api/v2/",
                issuer=f"https://{self.config.domain}/",
            )
        except Exception as error:
            raise UnauthorizedException(str(error))

        # if len(security_scopes.scopes) > 0:
        #     self._check_claims(payload, "scope", security_scopes.scopes)

        return payload

    # def _check_claims(self, payload, claim_name, expected_value):
    #     if claim_name not in payload:
    #         raise UnauthorizedException(
    #             detail=f'No claim "{claim_name}" found in token'
    #         )

    #     payload_claim = payload[claim_name]

    #     if claim_name == "scope":
    #         payload_claim = payload[claim_name].split(" ")

    #     for value in expected_value:
    #         if value not in payload_claim:
    #             raise UnauthorizedException(detail=f'Missing "{claim_name}" scope')
