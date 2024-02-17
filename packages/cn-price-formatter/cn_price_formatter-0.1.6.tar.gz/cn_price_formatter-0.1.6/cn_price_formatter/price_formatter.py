import json
from collections import defaultdict



class PriceFormatter:
    """
    PriceFormatter class for handling and formatting hotel pricing data.
    """

    def __init__(self):

        self.base_rate = 0
        self.avg_price_before_tax = 0
        self.avg_price_after_tax = 0
        self.total_tax_rate = 0
        self.rooms_available = 0
        self.room_count = 0
        self.tax_and_service_fee = 0
        self.extra_person_fee = 0
        self.property_fee = 0
        self.sales_tax = 0
        self.adjustment = 0
        self.recovery_charges_and_fees = 0
        self.traveler_service_fee = 0
        self.cn_fees = 0
        self.partner_total=0
        self.partner_tax=0
        self.total = 0
        self.total_tax = 0
        self.due_at_property = []
        self.mandatory_fee = 0
        self.mandatory_tax=0
        self.resort_fee = 0
        self.pay_now = 0
        self.cn_fee_percentage = 6
        self.number_of_nights = 0
    

    def hotel_planner(self, data: dict) -> None:
      """
      Parses and sets class variables based on hotel planner JSON data.

      Args:
          json_data (str): JSON data containing hotel pricing information.
      """
      # Validate if json_data is a string
      if not isinstance(data, dict):
          raise ValueError("Invalid input: json_data must be a dict.")


        # Validate the presence of required keys in the JSON data
      required_keys = ['totalBeforeTax', 'totalAfterTax', 'averageBeforeTax', 'averageAfterTax',
                      'totalTaxRate', 'roomsAvailable', 'roomCount', 'payNow']

      for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key '{key}' in the JSON data.")

      for key in required_keys:
        if not isinstance(data[key], (int, float, str)):
            raise ValueError(f"Invalid value for '{key}': Expecting a numeric value.")

        # Validate numeric values
      numeric_keys = ['totalBeforeTax', 'totalAfterTax', 'averageBeforeTax', 'averageAfterTax',
                      'totalTaxRate', 'roomsAvailable', 'roomCount', 'payNow']

      for key in numeric_keys:
          if not isinstance(data[key], (int, float)):
              raise ValueError(f"Invalid value for '{key}': Expecting a numeric value.")

      self.cn_fee_percentage = 6
      self.base_rate = data['totalBeforeTax']
      self.partner_total = data['totalAfterTax']
      self.avg_price_before_tax = data['averageBeforeTax']
      self.avg_price_after_tax = data['averageAfterTax']
      self.partner_tax = float(self.partner_total) - float(self.base_rate)
      self.total_tax_rate = data['totalTaxRate']
      self.cn_fees=self.get_total_cn_fee()
      self.total = self.partner_total+self.cn_fees
      self.total_tax = self.partner_tax + self.cn_fees
      self.rooms_available = data['roomsAvailable']

      self.room_count = data['roomCount']
      self.pay_now = self.total
      


    def expedia(self, json_data: dict) -> None:
        """
        Parses and sets class variables based on hotel planner JSON data.

        Args:
            json_data (str): JSON data containing hotel pricing information.
        """
        # Validate if json_data is a string
        if not isinstance(json_data, dict):
            raise ValueError("Invalid input: json_data must be a dict.")

        
        required_keys = ['nightly', 'fees', 'totals']
        for key in required_keys:
            if key not in json_data:
                raise ValueError(f"Missing key '{key}' in the JSON data.")
        
        
        base_rate = 0
        tax_and_service_fee = 0
        extra_person_fee = 0
        property_fee = 0
        sales_tax = 0
        adjustment = 0
        recovery_charges_and_fees = 0
        traveler_service_fee = 0
        mandatory_fee = 0
        resort_fee = 0
        mandatory_tax = 0
        due_at_property = []
        nightly_prices = []
        stay_prices = []
        total_expedia = 0
        


        nightly_prices = json_data.get('nightly',[])
        for other_taxes_data in nightly_prices:
            for row in other_taxes_data:
                exp_amount = float(row['value'])
                total_expedia += exp_amount
                if row['type'] == 'base_rate':
                    base_rate += exp_amount
                elif row['type'] == 'tax_and_service_fee':
                    tax_and_service_fee += exp_amount
                elif row['type'] == 'property_fee':
                    property_fee += exp_amount
                elif row['type'] == 'sales_tax':
                    sales_tax += exp_amount
                elif row['type'] == 'adjustment':
                    adjustment += exp_amount
                elif row['type'] == 'recovery_charges_and_fees':
                    recovery_charges_and_fees += exp_amount
                elif row['type'] == 'traveler_service_fee':
                    traveler_service_fee += exp_amount
                elif row['type'] == 'extra_person_fee':
                    extra_person_fee += exp_amount


        stay_prices = json_data.get('stay',[])
        if stay_prices:
            for row in stay_prices:
                tax_amount = float(row['value'])
                total_expedia += tax_amount
                if row['type'] == 'base_rate':
                    base_rate += tax_amount
                elif row['type'] == 'tax_and_service_fee':
                    tax_and_service_fee += tax_amount
                elif row['type'] == 'property_fee':
                    property_fee += tax_amount

                elif row['type'] == 'sales_tax':
                    sales_tax += tax_amount

                elif row['type'] == 'adjustment':
                    adjustment += tax_amount
                elif row['type'] == 'recovery_charges_and_fees':
                    recovery_charges_and_fees += tax_amount

                elif row['type'] == 'traveler_service_fee':
                    traveler_service_fee += tax_amount

                elif row['type'] == 'extra_person_fee':
                    extra_person_fee =+ tax_amount

        fees_price = json_data.get('fees',[])
        if fees_price:
            for f_key, row in fees_price.items():
                due_at_property.append(
                        {
                            "name": f_key,
                            "amount":float(row['request_currency']['value']),
                            "currency" : row['request_currency']['currency']
                        }
                    )
                if f_key == 'mandatory_fee':
                    mandatory_fee=float(row['request_currency']['value'])
                elif f_key == 'resort_fee':
                    resort_fee=float(row['request_currency']['value'])
                    

                elif f_key == 'mandatory_tax':
                    mandatory_tax=float(row['request_currency']['value'])
                    




        self.base_rate = base_rate
        self.tax_and_service_fee = tax_and_service_fee
        self.extra_person_fee = extra_person_fee
        self.property_fee = property_fee
        self.sales_tax = sales_tax
        self.adjustment = adjustment
        self.recovery_charges_and_fees = recovery_charges_and_fees
        self.traveler_service_fee = traveler_service_fee
        self.partner_total = total_expedia
        self.cn_fees = self.get_total_cn_fee()
        self.total = total_expedia + self.cn_fees
        self.total_tax= self.get_exp_total_tax()
        self.mandatory_fee=mandatory_fee
        self.resort_fee = resort_fee
        self.mandatory_tax=mandatory_tax
        self.due_at_property = due_at_property
        self.pay_now = self.total

    
    
    def rakuten(self, data: dict) -> None:
        """
        Parses and sets class variables based on rakuten JSON data.

        Args:
            json_data (str): JSON data containing hotel pricing information.
        """
        # Validate the structure of the JSON data
        if not isinstance(data, dict) or not data:
            raise ValueError("Invalid JSON structure: Expecting a non-empty list.")

        # Validate the presence of required keys in the JSON data
        required_keys = ['room_rate', 'client_commission']

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key '{key}' in the JSON data.")

            # Validate numeric values
        numeric_keys = ['room_rate', 'client_commission']

        for key in numeric_keys:
            if not isinstance(data[key], (int, float)):
                raise ValueError(f"Invalid value for '{key}': Expecting a numeric value.")

        self.base_rate = data["room_rate"]
        self.partner_tax=data["client_commission"]
        self.partner_total =  self.partner_tax+ self.base_rate
        self.cn_fees=self.get_total_cn_fee()
        self.total = self.partner_total + self.cn_fees
        self.total_tax = self.partner_tax + self.cn_fees

    def ratehawk(self, json_data):
        """
        Parses and sets class variables based on ratehawk JSON data.
        Args:
            json_data (str): JSON data containing hotel pricing information.
        """
        room_rate = 0
        partner_tax = 0
        # commenting for now
        due_at_property = []
        try:
            # Validate if json_data is a dictionary
            if not isinstance(json_data, dict):
                raise ValueError("Invalid input: json_data must be a dictionary.")
            # Validate the presence of required keys in the JSON data
            required_keys = ['rates']
            for key in required_keys:
                if key not in json_data:
                    raise ValueError(f"Missing key '{key}' in the JSON data.")
            # Validate the presence of required keys in the JSON data
            rates_data = json_data['rates'][0].get('payment_options', {}).get('payment_types', [])
            
            self.room_count  = json_data['rates'][0].get('allotment', 0)
            for payments in rates_data:
                try:
                    room_rate = payments.get("amount", 0)
                    vat_tax = payments.get('vat_data', {})
                    if vat_tax.get('included', True):
                        partner_tax += float(vat_tax.get('amount', 0))
                    # Check pay at property taxes
                    taxes_data = payments.get('tax_data', [])
                    if taxes_data:
                        for tax_data in taxes_data.get('taxes', []):
                            try:
                                if tax_data.get('included_by_supplier', True):
                                    partner_tax += float(tax_data.get('amount', 0))
                                else:
                                    # due_at_property += float(tax_data.get('amount', 0))
                                    due_at_property.append({
                                        'name' : tax_data['name'],
                                        'amount': float(tax_data.get('amount', 0)),
                                        'currency': tax_data.get('currency_code', '')
                                    }) 
                            except (KeyError, ValueError) as e:
                                raise ValueError(f"Error processing tax data: {e}")
                except (KeyError, TypeError) as e:
                    raise ValueError(f"Error accessing JSON data: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")
        self.base_rate = room_rate
        self.partner_tax = partner_tax
        self.partner_total  =  self.base_rate+ self.partner_tax
        self.cn_fees = self.get_total_cn_fee()
        self.total= self.partner_total+self.cn_fees
        self.total_tax = self.partner_tax+ self.cn_fees
        self.due_at_property = due_at_property
        
    def didatravel(self, data: dict) -> None:
        """
        Parses and sets class variables based on hotel planner JSON data.

        Args:
            json_data (str): JSON data containing hotel pricing information.
        """

        if not isinstance(data, dict) or not data:
            raise ValueError("Invalid JSON structure: Expecting a non-empty list.")

        # Validate the presence of required keys in the JSON data
        required_keys = ['TotalPrice', 'PriceList']

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key '{key}' in the JSON data.")

        
                   
        
    

        base_rate = data["TotalPrice"]
        number_of_nights = len(data['PriceList'])
        totalPrice = base_rate
        self.base_rate = base_rate
        self.partner_total = base_rate
        self.cn_fees = self.get_total_cn_fee()
        self.total = self.partner_total + self.cn_fees
        self.total_tax = self.cn_fees
        price_per_night = totalPrice / number_of_nights
        self.price_per_night = price_per_night
        self.pay_now = self.total



    def hp_get_room_date_wise(self, data) -> None:
        """
        Parses and organizes room data by effectiveDate from hotel planner JSON data.

        Args:
            json_data (str): JSON data containing hotel room pricing information.
        """

        # Organize data by effectiveDate
        effective_dates_data: defaultdict[str, dict] = defaultdict(lambda: {"totalBeforeTax": [], "totalAfterTax": []})
        
        for rate in data[0]["rates"]:
            effective_date = rate["effectiveDate"]
            effective_dates_data[effective_date]["totalBeforeTax"].append(rate["totalBeforeTax"])
            effective_dates_data[effective_date]["totalAfterTax"].append(rate["totalAfterTax"])

    def get_base_rate(self) -> float:
            """
            Returns the total price before tax.

            Returns:
                float: Total price before tax.
            """
            # Validate that base_rate is a numeric value
            if not isinstance(self.base_rate, (int, float)):
                raise ValueError("Invalid value for base_rate: Expecting a numeric value.")
            return self.base_rate

    def get_total_price(self) -> float:
        """
        Returns the total price after tax.

        Returns:
            float: Total price after tax.
        """
        # Validate that total is a numeric value
        if not isinstance(self.total, (int, float)):
            raise ValueError("Invalid value for total: Expecting a numeric value.")
        return self.total

    def get_avg_price_before_tax(self) -> float:
        """
        Returns the average price before tax.

        Returns:
            float: Average price before tax.
        """
        # Validate that avg_price_before_tax is a numeric value
        if not isinstance(self.avg_price_before_tax, (int, float)):
            raise ValueError("Invalid value for avg_price_before_tax: Expecting a numeric value.")
        return self.avg_price_before_tax

    def get_avg_price_after_tax(self) -> float:
        """
        Returns the average price after tax.

        Returns:
            float: Average price after tax.
        """
        # Validate that avg_price_after_tax is a numeric value
        if not isinstance(self.avg_price_after_tax, (int, float)):
            raise ValueError("Invalid value for avg_price_after_tax: Expecting a numeric value.")
        return self.avg_price_after_tax

    def get_total_tax(self) -> float:
        """
        Returns the total tax amount.

        Returns:
            float: Total tax amount.
        """
        # Validate that total_tax is a numeric value
        if not isinstance(self.total_tax, (int, float)):
            raise ValueError("Invalid value for total_tax: Expecting a numeric value.")
        return self.total_tax

    def get_total_cn_fee(self) -> float:
        """
        Returns the total CN fee based on the total price after tax and CN fee percentage.

        Returns:
            float: Total CN fee.
        """
        # Validate that total and cn_fee_percentage are numeric values
        if not isinstance(self.partner_total, (int, float)):
            raise ValueError("Invalid value for total: Expecting a numeric value.")
        if not isinstance(self.cn_fee_percentage, (int, float)):
            raise ValueError("Invalid value for cn_fee_percentage: Expecting a numeric value.")
        
        return (self.partner_total / 100) * self.cn_fee_percentage

    def get_exp_total_tax(self):
      """
      Returns the total expedia tax based on tax_and_service_fee, extra_person_fee,property_fee,sales_tax,recovery_charges_and_fees,traveler_service_fee and cn_fees.

      Returns:
          float: Total Exp Tax
        """
      if not isinstance(self.tax_and_service_fee, (int, float)):
            raise ValueError("Invalid value for total: Expecting a numeric value for tax and service fee.")
      if not isinstance(self.extra_person_fee, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for extra person fee.")
      if not isinstance(self.property_fee, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for property fee.")
      if not isinstance(self.sales_tax, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for sales tax.")
      if not isinstance(self.recovery_charges_and_fees, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for revovery service charges and fees.")
      if not isinstance(self.traveler_service_fee, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for traveler service fee.")
      if not isinstance(self.cn_fees, (int, float)):
        raise ValueError("Invalid value for total: Expecting a numeric value for cn fees.")
      if not isinstance(self.cn_fee_percentage, (int, float)):
          raise ValueError("Invalid value for cn_fee_percentage: Expecting a numeric value.")

      return self.tax_and_service_fee + self.extra_person_fee + self.property_fee + self.sales_tax  + self.recovery_charges_and_fees + self.traveler_service_fee+self.cn_fees
