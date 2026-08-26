from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
)

from frame.domain.transaction import (
    Transaction,
)


class RiskScoreRequest(BaseModel):
    transaction_id: str

    customer_id: str
    merchant_id: str
    device_id: str
    card_id: str
    ip_id: str

    amount: float = Field(
        gt=0
    )

    timestamp: datetime

    account_age_days: int = (
        Field(
            ge=0
        )
    )

    def to_transaction(
        self,
    ) -> Transaction:
        return Transaction(
            transaction_id=(
                self.transaction_id
            ),
            customer_id=(
                self.customer_id
            ),
            merchant_id=(
                self.merchant_id
            ),
            device_id=(
                self.device_id
            ),
            card_id=(
                self.card_id
            ),
            ip_id=(
                self.ip_id
            ),
            amount=(
                self.amount
            ),
            timestamp=(
                self.timestamp
            ),
            account_age_days=(
                self.account_age_days
            ),
        )