from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    SECURE_COOKIES: bool = True


auth_config = AuthConfig()
