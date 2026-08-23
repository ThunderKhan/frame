from pydantic import ValidationError
import pytest

from frame.domain.customer import CustomerProfile


def test_valid_customer_profile() -> None:
    customer = CustomerProfile(
        customer_id="cust_00001",
        card_ids=["card_00001"],
        device_ids=["device_00001"],
        ip_ids=["ip_00001"],
        account_age_days=200,
    )

    assert customer.customer_id == "cust_00001"
    assert len(customer.card_ids) == 1
    assert len(customer.device_ids) == 1
    assert len(customer.ip_ids) == 1


def test_customer_requires_at_least_one_card() -> None:
    with pytest.raises(ValidationError):
        CustomerProfile(
            customer_id="cust_00001",
            card_ids=[],
            device_ids=["device_00001"],
            ip_ids=["ip_00001"],
            account_age_days=200,
        )