from elena.adapters.storage_manager.file_storage_manager import FileStorageManager, Record
from elena.domain.model.order_book import PriceAmount


def test_to_record_with_pydantic_base_model():
    actual = FileStorageManager._to_record(
        data_id="id",
        data=PriceAmount(
            price=1.664123,
            amount=1584.3333,
        ),
    )
    assert actual == Record(
        id="id",
        class_name="PriceAmount",
        class_module="elena.domain.model.order_book",
        value={
            "price": 1.664123,
            "amount": 1584.3333,
        },
        name="PriceAmount",
    )


def test_from_record_with_pydantic_base_model():
    actual = FileStorageManager._from_record(
        Record(
            id="id",
            class_name="PriceAmount",
            class_module="elena.domain.model.order_book",
            value={
                "price": 1.664123,
                "amount": 1584.3333,
            },
            name="PriceAmount",
        )
    )
    assert actual == PriceAmount(
        price=1.664123,
        amount=1584.3333,
    )
