import re
from typing import Annotated

from pydantic import EmailStr, Field, field_validator
from pydantic.types import StringConstraints

from src.auth.exceptions import InvalidPassoword
from src.models import CustomModel

STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$")


class AuthUser(CustomModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise InvalidPassoword
        return password


class UserResponse(CustomModel):
    email: EmailStr
    id: int


class UserUpdateSchema(CustomModel):
    email: EmailStr | None = None
    password: Annotated[str, StringConstraints(min_length=6, max_length=128)] | None = None
