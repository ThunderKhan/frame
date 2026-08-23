from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    customer_id: str

    card_ids: list[str] = Field(min_length=1)
    device_ids: list[str] = Field(min_length=1)
    ip_ids: list[str] = Field(min_length=1)

    account_age_days: int = Field(ge=0)