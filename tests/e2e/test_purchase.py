import pytest
from playwright.sync_api import Page

from src.pages.home_page import HomePage


@pytest.mark.e2e
@pytest.mark.purchase
def test_purchase(buyer_page: Page) -> None:
    order_confirmation = (
        HomePage(buyer_page)
        .add_first_product_to_basket()
        .open_basket()
        .checkout()
        .select_first_address()
        .proceed()
        .select_first_delivery_method()
        .proceed()
        .select_first_card()
        .proceed()
        .place_order()
    )

    order_confirmation.assert_order_created()
