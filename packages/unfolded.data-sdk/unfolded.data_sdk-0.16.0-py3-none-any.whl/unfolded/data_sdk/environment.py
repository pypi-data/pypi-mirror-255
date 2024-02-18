from enum import Enum

from pydantic import BaseModel


class EnvironmentConfig(BaseModel):
    """EnvironmentConfig specifies request and authentication endpoints for a given environment"""

    base_url: str = "https://data-api.foursquare.com"
    studio_url: str = "https://studio.foursqure.com"


class AuthEnvironment(str, Enum):
    """Enum for the different Unfolded environments"""

    PRODUCTION = "production"
    PRODUCTION_NO_ROTATE = "production-no-rotate"


class AuthConfig(BaseModel):
    client_id: str
    auth_url: str = "https://auth.studio.foursquare.com"
    audience: str = "https://foursquare.com/api/"
    scope: str = "offline_access"


AUTH_CONFIGS = {
    AuthEnvironment.PRODUCTION: AuthConfig(
        client_id="v970dpbcqmRtr3y9XwlAB3dycpsvNRZF",
    ),
    AuthEnvironment.PRODUCTION_NO_ROTATE: AuthConfig(
        client_id="75nXztDByx9A3525kDyTAqDeLSMWEwyj",
    ),
}

PRODUCTION_ENV = EnvironmentConfig()
