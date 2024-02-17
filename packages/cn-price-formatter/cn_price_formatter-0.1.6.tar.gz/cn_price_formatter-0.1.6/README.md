# PriceFormatter Package

This package provides a PriceFormatter class for handling and formatting hotel pricing data.


# PriceFormatter Class

The `PriceFormatter` class is designed to handle and format hotel pricing data. It includes methods for parsing hotel planner JSON data and organizing room data by effective date.

## Usage

from price_formatter import PriceFormatter

# Initialize PriceFormatter
formatter = PriceFormatter()

## Hotel Planner Data
hotel_planner_data = '''[
        {
          "averageBeforeTax": 113.5,
          "isGovernment": false,
          "totalTaxRate": 0.21897,
          "ratePlanCode": "270271687",
          "cancelPolicy": {
            "nonRefundable": true,
            "description": "",
            "cancelPenalties": [
              {
                "deadline": "01/02/2024",
                "noShow": false,
                "price": 374.15
              }
            ],
            "text": "NONREFUNDABLE",
            "timezoneTag": "LOCAL HOTEL TIME",
            "freeCancellation": false,
            "prePaid": true
          },
          "earnings": {
            "currencyCode": "USD"
          },
          "isMilitary": false,
          "fees": [],
          "totalAfterTax": 444.41,
          "roomsAvailable": 1,
          "payNow": true,
          "bundle": "",
          "totalBeforeTax": 341.97,
          "roomTypeCode": "217519820",
          "isSenior": false,
          "isFlRes": false,
          "averageAfterTax": 148.14,
          "roomCount": 1,
          "isAaa": false,
          "promotionText": "Book now and save",
          "isAvailable": true
        }
      ]'''

## Parse Hotel Planner Data
formatter.hotel_planner(hotel_planner_data)

## Get Total Price Before Tax
total_price_before_tax = formatter.get_total_price_before_tax()
print(f"Total Price Before Tax: {total_price_before_tax}")

## Get Total Price After Tax
total_price_after_tax = formatter.get_total_price_after_tax()
print(f"Total Price After Tax: {total_price_after_tax}")

## Get Average Price Before Tax
avg_price_before_tax = formatter.get_avg_price_before_tax()
print(f"Average Price Before Tax: {avg_price_before_tax}")

## Get Average Price After Tax
avg_price_after_tax = formatter.get_avg_price_after_tax()
print(f"Average Price After Tax: {avg_price_after_tax}")

## Get Total Tax
total_tax = formatter.get_total_tax()
print(f"Total Tax: {total_tax}")

## Get Total CN Fee
total_cn_fee = formatter.get_total_cn_fee()
print(f"Total CN Fee: {total_cn_fee}")


## Installation

You can install the package using pip:

`pip install cn-price-formatter`

