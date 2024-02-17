import json
import pytest
from cn_price_formatter.price_formatter import PriceFormatter

@pytest.fixture
def sample_json_data():
    json_data = '''
        {
        "id": "test_hotel",
        "rates": [
            {
            "match_hash": "m-755ad68a-a3f9-5ba2-a808-8ef15ce55434",
            "daily_prices": ["45.00"],
            "meal": "nomeal",
            "payment_options": {
                "payment_types": [
                {
                    "amount": "45.00",
                    "show_amount": "45.00",
                    "currency_code": "USD",
                    "show_currency_code": "USD",
                    "by": null,
                    "is_need_credit_card_data": false,
                    "is_need_cvc": false,
                    "type": "deposit",
                    "vat_data": {
                    "included": false,
                    "applied": false,
                    "amount": "0.00",
                    "currency_code": "RUB",
                    "value": "0.00"
                    },
                    "tax_data": {
                    "taxes": [
                        {"name": "city_tax", "included_by_supplier": false, "amount": "100.00", "currency_code": "RUB"},
                        {"name": "cleaning_fee", "included_by_supplier": false, "amount": "1000.00", "currency_code": "RUB"},
                        {"name": "luxury_tax", "included_by_supplier": false, "amount": "5000.00", "currency_code": "RUB"},
                        {"name": "resort_fee", "included_by_supplier": false, "amount": "300.00", "currency_code": "RUB"},
                        {"name": "service_fee", "included_by_supplier": false, "amount": "880.00", "currency_code": "RUB"},
                        {"name": "vat", "included_by_supplier": false, "amount": "220.00", "currency_code": "RUB"}
                    ]
                    }
                }
                ],
                "perks": {},
                "commission_info": {
                "show": {"amount_gross": "45.00", "amount_net": "45.00", "amount_commission": "0.00"},
                "charge": {"amount_gross": "45.00", "amount_net": "45.00", "amount_commission": "0.00"}
                },
                "cancellation_penalties": {
                "policies": [
                    {"start_at": null, "end_at": "2024-03-23T03:00:00", "amount_charge": "0.00", "amount_show": "0.00",
                    "commission_info": {"show": {"amount_gross": "0.00", "amount_net": "0.00", "amount_commission": "0.00"},
                                        "charge": {"amount_gross": "0.00", "amount_net": "0.00", "amount_commission": "0.00"}}},
                    {"start_at": "2024-03-23T03:00:00", "end_at": null, "amount_charge": "45.00", "amount_show": "45.00",
                    "commission_info": {"show": {"amount_gross": "45.00", "amount_net": "45.00", "amount_commission": "0.00"},
                                        "charge": {"amount_gross": "45.00", "amount_net": "45.00", "amount_commission": "0.00"}}}
                ],
                "free_cancellation_before": "2024-03-23T03:00:00"
                },
                "recommended_price": null
            }
            }
        ],
        "bar_rate_price_data": null,
        "rg_ext": {
            "class": 5,
            "quality": 0,
            "sex": 0,
            "bathroom": 2,
            "bedding": 0,
            "family": 0,
            "capacity": 0,
            "club": 0,
            "bedrooms": 1,
            "balcony": 0,
            "view": 0,
            "floor": 0
        },
        "room_name": "1 Bedroom Suite",
        "serp_filters": ["has_bathroom"],
        "sell_price_limits": null,
        "allotment": 1,
        "amenities_data": ["1-bedroom", "non-smoking"],
        "any_residency": true,
        "deposit": null,
        "no_show": {"amount": "4400.00", "currency_code": "RUB", "from_time": "12:00:00"},
        "room_data_trans": {"main_room_type": "1 Bedroom Suite", "main_name": "1 Bedroom Suite", "bathroom": null,
        "bedding_type": null, "misc_room_type": null}
        }
    '''
    return json_data

def test_initialization():
    formatter = PriceFormatter()
    assert formatter.base_rate == 0
    assert formatter.total == 0
    assert formatter.total_tax == 0
    assert formatter.total_tax_rate == 0
    assert formatter.cn_fees == 0
    assert formatter.due_at_property==[]

def test_ratehawk_valid_json(json_data):
    formatter = PriceFormatter()
    
    json_data = json.loads(json_data)
    formatter.ratehawk(json_data)
    assert formatter.base_rate == 45.00
    assert formatter.total == 45.00
    
def test_get_base_rate():
    formatter = PriceFormatter()
    formatter.base_rate = 45.00
    assert formatter.get_base_rate() == 45.00

def test_get_total_cn_fee(json_data):
    
    ratehawk = PriceFormatter()
    ratehawk.ratehawk(json_data)
    ratehawk.get_total_cn_fee()
    assert ratehawk.get_total_cn_fee() == 2.7
