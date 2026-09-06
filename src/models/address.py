from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    full_name: str
    mobile_number: int
    zip_code: str
    street_address: str
    city: str
    state: str
    country: str
