from datetime import datetime

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str

    customer_id: str
    merchant_id: str
    device_id: str
    card_id: str
    ip_id: str

    amount: float = Field(gt=0)
    timestamp: datetime

    account_age_days: int = Field(ge=0)

    is_fraud: bool = False
    fraud_ring_id: str | None = None