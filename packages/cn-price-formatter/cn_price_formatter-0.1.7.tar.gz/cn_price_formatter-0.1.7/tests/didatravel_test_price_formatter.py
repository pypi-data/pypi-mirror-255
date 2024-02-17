import pytest
from cn_price_formatter.price_formatter import PriceFormatter

@pytest.fixture
def sample_didatravel_json_data():
    json_data = {
                     "TotalPrice":373.64,
                     "RoomStatus":1,
                     "BreakfastType":2,
                     "BedType":2,
                     "RoomOccupancy":{
                        "ChildCount":0,
                        "AdultCount":2,
                        "RoomNum":1
                     },
                     "PriceList":[
                        {
                           "StayDate":"2024-02-09 00:00:00",
                           "Price":186.82
                        },
                        {
                           "StayDate":"2024-02-10 00:00:00",
                           "Price":186.82
                        }
                     ],
                     "RatePlanCancellationPolicyList":[
                        {
                           "Amount":373.64,
                           "FromDate":"2024-02-07 00:00:00"
                        }
                     ],
                     "StandardOccupancy":2,
                     "InventoryCount":99,
                     "MaxOccupancy":2,
                     "RoomTypeID":10324947,
                     "Currency":"USD",
                     "RatePlanName":"Double room",
                     "RatePlanID":"3974443229724117686",
                     "RoomName":"Standard Double Room"
                  }   

                  
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

    
def test_didatravel_valid_json(sample_didatravel_json_data):
    formatter = PriceFormatter()
    formatter.didatravel(sample_didatravel_json_data)
    assert formatter.total == 396.0584
    assert formatter.base_rate == 373.64
    

def test_didatravel_invalid_json():
    formatter = PriceFormatter()
    with pytest.raises(ValueError, match="Invalid JSON data"):
        formatter.didatravel("invalid_json")


def test_get_total_price_before_tax():
    formatter = PriceFormatter()
    formatter.base_rate = 341.97
    assert formatter.get_base_rate() == 341.97

    
def test_get_total_cn_fee_didatravel(sample_didatravel_json_data):
    didatravel = PriceFormatter()
    didatravel.didatravel(sample_didatravel_json_data)
    assert didatravel.get_total_cn_fee() == 22.4184
    
    
  
  
  