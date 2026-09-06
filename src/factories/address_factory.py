from faker import Faker

from src.models.address import Address

_faker = Faker()


class AddressFactory:
    @staticmethod
    def build() -> Address:
        return Address(
            full_name=_faker.name(),
            mobile_number=_faker.random_number(digits=10),
            zip_code=_faker.postalcode(),
            street_address=_faker.street_address(),
            city=_faker.city(),
            state=_faker.state(),
            country=_faker.country(),
        )
