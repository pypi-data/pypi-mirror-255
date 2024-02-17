import json
import pytest
from cn_price_formatter.price_formatter import PriceFormatter

@pytest.fixture
def sample_json_data():
    json_data = {
          "averageBeforeTax": 113.5,
          "isGovernment": "false",
          "totalTaxRate": 0.21897,
          "ratePlanCode": "270271687",
          "cancelPolicy": {
            "nonRefundable": "true",
            "description": "",
            "cancelPenalties": [
              {
                "deadline": "01/02/2024",
                "noShow": "false",
                "price": 374.15
              }
            ],
            "text": "NONREFUNDABLE",
            "timezoneTag": "LOCAL HOTEL TIME",
            "freeCancellation": "false",
            "prePaid": "true"
          },
          "earnings": {
            "currencyCode": "USD"
          },
          "isMilitary": "false",
          "fees": [],
          "totalAfterTax": 444.41,
          "roomsAvailable": 1,
          "payNow": "true",
          "bundle": "",
          "rates": [
            {
              "totalBeforeTax": 113.99,
              "extraPersonFee": 0,
              "totalExtraPersonFees": 0.0,
              "effectiveDate": "2024-02-12",
              "expireDate": "2024-02-13",
              "duration": 1.0,
              "amountAfterTax": 148.14,
              "amountBeforeTax": 113.99,
              "totalAfterTax": 148.14
            },
            {
              "totalBeforeTax": 113.99,
              "extraPersonFee": 0,
              "totalExtraPersonFees": 0.0,
              "effectiveDate": "2024-02-13",
              "expireDate": "2024-02-14",
              "duration": 1.0,
              "amountAfterTax": 148.14,
              "amountBeforeTax": 113.99,
              "totalAfterTax": 148.14
            },
            {
              "totalBeforeTax": 113.99,
              "extraPersonFee": 0,
              "totalExtraPersonFees": 0.0,
              "effectiveDate": "2024-02-14",
              "expireDate": "2024-02-15",
              "duration": 1.0,
              "amountAfterTax": 148.13,
              "amountBeforeTax": 113.99,
              "totalAfterTax": 148.13
            }
          ],
          "totalBeforeTax": 341.97,
          "roomTypeCode": "217519820",
          "isSenior": "false",
          "isFlRes": "false",
          "averageAfterTax": 148.14,
          "roomCount": 1,
          "isAaa": "false",
          "promotionText": "Book now and save",
          "isAvailable": "true"
        }
      
    return json_data

def test_initialization():
    formatter = PriceFormatter()
    assert formatter.base_rate == 0
    assert formatter.property_fee == 0
    assert formatter.sales_tax == 0
    assert formatter.cn_fees == 0
    assert formatter.total_tax == 0
    assert formatter.total == 0
    assert formatter.rooms_available == 0
    assert formatter.room_count == 0
    assert formatter.pay_now == 0
    assert formatter.cn_fees == 0

def test_hotel_planner_valid_json(sample_json_data):
    formatter = PriceFormatter()
    formatter.hotel_planner(sample_json_data)
    assert formatter.base_rate == 341.97
    assert formatter.total == 471.07460000000003
    
def test_hotel_planner_invalid_json():
    formatter = PriceFormatter()
    with pytest.raises(ValueError, match="Invalid JSON data"):
        formatter.hotel_planner("invalid_json")

def test_get_total_price_before_tax():
    formatter = PriceFormatter()
    formatter.base_rate = 341.97
    assert formatter.get_base_rate() == 341.97

def test_get_total_cn_fee(sample_json_data):
    hotel_planner = PriceFormatter()
    hotel_planner.hotel_planner(sample_json_data)
    hotel_planner.get_total_cn_fee()
    assert hotel_planner.get_total_cn_fee() == 26.664600000000004