from app.services.lead_mapper import (
    map_meta_lead_to_create,
    normalize_field_data,
)


def test_normalize_field_data():
    field_data = [
        {"name": "full_name", "values": ["John Doe"]},
        {"name": "email", "values": ["john@example.com"]},
        {"name": "phone_number", "values": ["9876543210"]},
    ]
    result = normalize_field_data(field_data)
    assert result == {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone_number": "9876543210",
    }


def test_normalize_field_data_empty():
    assert normalize_field_data([]) == {}


def test_normalize_field_data_skip_missing_values():
    field_data = [
        {"name": "full_name", "values": []},
        {"name": "email", "values": ["john@example.com"]},
    ]
    result = normalize_field_data(field_data)
    assert result == {"email": "john@example.com"}


def test_map_meta_lead_to_create():
    meta_response = {
        "id": "987654321",
        "form_id": "555555",
        "ad_id": "777777",
        "field_data": [
            {"name": "full_name", "values": ["John Doe"]},
            {"name": "email", "values": ["john@example.com"]},
            {"name": "phone_number", "values": ["9876543210"]},
        ],
    }
    result = map_meta_lead_to_create(
        meta_data=meta_response,
        page_id="page-123",
        form_id="form-456",
        ad_id="ad-789",
    )
    assert result.meta_lead_id == "987654321"
    assert result.page_id == "page-123"
    assert result.form_id == "form-456"
    assert result.ad_id == "ad-789"
    assert result.full_name == "John Doe"
    assert result.email == "john@example.com"
    assert result.phone_number == "9876543210"
    assert result.raw_payload == meta_response


def test_map_meta_lead_to_create_first_last_name():
    meta_response = {
        "id": "111222333",
        "form_id": "form-1",
        "field_data": [
            {"name": "first_name", "values": ["Jane"]},
            {"name": "last_name", "values": ["Smith"]},
        ],
    }
    result = map_meta_lead_to_create(
        meta_data=meta_response,
        page_id="page-1",
        form_id=None,
        ad_id=None,
    )
    assert result.meta_lead_id == "111222333"
    assert result.full_name == "Jane Smith"