import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_storefront_shows_products(storefront: Page) -> None:
    expect(storefront.get_by_role("button", name="Add to Basket").first).to_be_visible()
