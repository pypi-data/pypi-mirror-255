import json
import pytest
from cn_price_formatter.price_formatter import PriceFormatter

@pytest.fixture
def sample_json_data():
    json_data = {'hotel_id': 'SZqK', 'room_details': {'room_code': '0100111107', 'rate_plan_code': '5a7c86b5457d', 'rate_plan_description': None, 'description': 'Standard Room Double Bed', 'food': 1, 'non_refundable': True, 'room_type': 'Standard', 'room_view': '', 'beds': {'double': 1}, 'supplier_description': 'DOUBLE WITH TERRACE', 'non_smoking': None, 'room_gender': None, 'benefits': None, 'floor': None, 'amenitites': None}, 'booking_key': '53d19bf9', 'room_rate': 987.57, 'room_rate_currency': 'USD', 'client_commission': 0, 'client_commission_currency': 'USD', 'chargeable_rate': 987.57, 'chargeable_rate_currency': 'USD', 'cancellation_policy': {'remarks': '', 'cancellation_policies': [{'penalty_percentage': 100, 'date_from': '2024-01-29T22:59:00Z', 'date_to': '2024-03-18T00:00:00Z'}]}, 'rate_type': 'net', 'daily_number_of_units': None, 'created_at': '2024-01-31T11:13:50.114609566Z'}
    
    return json_data

def test_initialization():
    formatter = PriceFormatter()
    assert formatter.base_rate == 0
    assert formatter.total == 0
    assert formatter.avg_price_before_tax == 0
    assert formatter.avg_price_after_tax == 0
    assert formatter.total_tax == 0
    assert formatter.total_tax_rate == 0
    assert formatter.rooms_available == 0
    assert formatter.room_count == 0
    assert formatter.pay_now == 0
    assert formatter.cn_fees == 0

# def test_rakuten_valid_json():
#     formatter = PriceFormatter()
#     formatter.rakuten(sample_json_data)
#     assert formatter.base_rate == 987.57
#     assert formatter.total == 987.57
    
def test_get_total_price_before_tax():
    formatter = PriceFormatter()
    formatter.base_rate = 987.57
    assert formatter.get_base_rate() == 987.57

def test_get_total_cn_fee(sample_json_data):
    rakuten = PriceFormatter()
    rakuten.rakuten(sample_json_data)
    rakuten.get_total_cn_fee()
    assert rakuten.get_total_cn_fee() == 59.2542

