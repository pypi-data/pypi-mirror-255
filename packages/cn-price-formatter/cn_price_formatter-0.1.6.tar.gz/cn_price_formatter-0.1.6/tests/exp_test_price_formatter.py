import json
import pytest
from cn_price_formatter.price_formatter import PriceFormatter

@pytest.fixture
def sample_json_data():
    json_data = """{
  "nightly": [
    [
      {
        "type": "base_rate",
        "value": "539.08",
        "currency": "USD"
      },
      {
        "type": "tax_and_service_fee",
        "value": "121.30",
        "currency": "USD"
      }
    ]
  ],
  "fees": {
    "mandatory_tax": {
      "request_currency": {
        "value": "5.45",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "20.00",
        "currency": "AED"
      }
    }
  },
  "totals": {
    "exclusive": {
      "request_currency": {
        "value": "539.08",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "539.08",
        "currency": "USD"
      }
    },
    "gross_profit": {
      "request_currency": {
        "value": "75.25",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "75.25",
        "currency": "USD"
      }
    },
    "inclusive": {
      "request_currency": {
        "value": "660.38",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "660.38",
        "currency": "USD"
      }
    },
    "property_fees": {
      "request_currency": {
        "value": "5.45",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "20.00",
        "currency": "AED"
      }
    },
    "marketing_fee": {
      "request_currency": {
        "value": "39.88",
        "currency": "USD"
      },
      "billable_currency": {
        "value": "39.88",
        "currency": "USD"
      }
    }
  }
}"""
    return json.loads(json_data)

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

def test_expedia_valid_json(sample_json_data):
    formatter = PriceFormatter()
    formatter.expedia(sample_json_data)
    assert formatter.base_rate == 539.08
    assert formatter.total == 700.0028
    
# def test_expedia_invalid_json():
#     formatter = PriceFormatter()
    
#     with pytest.raises(ValueError, match="Invalid JSON data"):
#         formatter.expedia("invalid_json")

def test_get_total_price_before_tax():
    formatter = PriceFormatter()
    formatter.base_rate = 539.08
    assert formatter.get_base_rate() == 539.08

def test_get_total_cn_fee_expedia(sample_json_data):
    formatter = PriceFormatter()
    formatter.expedia(sample_json_data)
    assert formatter.get_total_cn_fee() == 39.6228