# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.signalmanager import dispatcher
from scrapy import signals

class MergedDataPipeline:
    def __init__(self):
        self.raw_data = []
        self.cleaned_data = []
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('source'):
            #Process raw data
            self.raw_data.append(adapter.asdict())

            #Process cleaned data
            cleaned_item = self.clean_item(item)
            self.cleaned_data.append(cleaned_item)
        return item
    def close_spider(self,spider):

        #Process data
        spider.log("pipeline Closing spider and sending custom_closed_signal...")
        dispatcher.send(signal=signals.spider_closed, 
                        sender=spider, 
                        cleaned_data = self.cleaned_data, 
                        raw_data = self.raw_data)


    def clean_item(self, item):

        if item.get("available_from") =="As soon as possible":
            item["available_from"] = item.get("creation_date")

        # Transform "Available from" field to Unix timestamp
        item['available_from'] = self.convert_date_to_unix_timestamp(item.get('available_from'))

        # Transform "Creation Date" field to Unix timestamp
        item['creation_date'] = self.convert_date_to_unix_timestamp(item.get('creation_date'))

        # Transform boolean values
        bool_keys = ['furnished', 'shareable', 'pets_allowed', 'elevator', 'senior_friendly', 'students_only', 'balcony', 'parking', 'dishwasher', 'washing_machine', 'electric_charging_station', 'dryer']
        for key in bool_keys:
            item[key] = self.to_boolean(item.get(key))

        # Convert numeric fields to integers
        int_keys = ['size', 'rooms','listing-id']
        for key in int_keys:
            item[key] = self.to_integer(item.get(key))

        # Convert prices to float
        float_keys =['monthly_net_rent', 'utilities', 'deposit', 'prepaid_rent', 'move-in_price','housing_deposit']
        for key in float_keys:
            item[key] = self.to_float(item.get(key))

        #Convert "Floor" values to integers
        item['floor'] = self.map_floor_to_integer(item['floor'])

        # Convert "-" to None
        for key,value in item.items():
            if value =='-':
                item[key] = None
        
        self.cleaned_data.append(item)
        return item
    
    def convert_date_to_unix_timestamp(self, date_str):
        try:
            # Specify the format for "01 February 2024"
            date_formats = ["%d %B %Y", "%d %b %Y","%d/%m/%Y"]  # You can add more formats as needed
            for date_format in date_formats:
                try:
                    date_object = datetime.strptime(date_str, date_format)
                    unix_timestamp = int(date_object.timestamp())
                    return unix_timestamp
                except ValueError:
                    pass
            return None  # Return None if no valid format is found
        except Exception as e:
            return None
        
    def to_boolean(self, value):
        if value == "Yes":
            return True
        elif value == "No":
            return False
        else:
            return None

    def to_integer(self, value):
        try:
            return int(value.replace(' m²', '').replace(',', '').replace('.', ''))
        except ValueError:
            return None
        
    def to_float(self, value):
        if value is None:
            return
        try:
            return float(value.replace('.','').replace(',','.').replace(' kr', ''))
        except ValueError:
            return None

    def map_floor_to_integer(self, floor):
        floor = floor.strip().lower()
        if floor == "ground floor":
            return 0
        elif floor[:-2].isdigit():
            return int(floor[:-2])
        else:
            return None
    