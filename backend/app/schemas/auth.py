
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    organization_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password must not start or end with whitespace")

        if any(ord(char) < 32 for char in value):
            raise ValueError("Password contains invalid control characters")

        return value

    @field_validator("full_name", "organization_name")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Field cannot be blank")

        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

