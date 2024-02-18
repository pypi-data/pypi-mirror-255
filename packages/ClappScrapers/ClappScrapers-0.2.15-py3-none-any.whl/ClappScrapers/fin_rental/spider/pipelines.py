# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import re
from scrapy import signals
from scrapy.signalmanager import dispatcher


def clean_number(number):

    if number is None:
        return ""
    
    cleaned_number = number.replace("€","").replace(",","").replace('','').strip()

    return cleaned_number



class MergedDataPipeline:
    def __init__(self):
        self.raw_data = []
        self.cleaned_data = []
        self.list_dic = {}

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('source'):
            
            #Process raw data
            self.raw_data.append(adapter.asdict())

            #Process cleaned data
            cleaned_item = self.clean_item(item)
            self.cleaned_data.append(cleaned_item)

        return item
    
    def close_spider(self, spider):
        # Convert values to list for keys in list_dic
        for key in self.list_dic:
            for cleaned_item in self.cleaned_data:
                self.convert_to_list(cleaned_item, key)

        # Process data
        spider.log("Closing spider and sending custom_closed_signal...")
        dispatcher.send(
            signal=signals.spider_closed,
            sender=spider,
            cleaned_data=self.cleaned_data,
            raw_data=self.raw_data,
            list_dic=self.list_dic
        )

    
    def convert_to_list(self, cleaned_item, key):

        # Recursive function to convert values to list for a specific key
        if isinstance(cleaned_item, dict):
            for sub_key, sub_value in cleaned_item.items():
                if sub_key == key and sub_key in self.list_dic:
                    cleaned_item[sub_key] = [sub_value] if not isinstance(sub_value, list) else sub_value
                elif isinstance(sub_value,(dict, list)):
                    self.convert_to_list(sub_value, key)
        elif isinstance(cleaned_item, list):
            for element in cleaned_item:
                self.convert_to_list(element, key)

    def clean_item (self,item):

        if isinstance(item, dict):
            cleaned_item = {}
            for key, value in item.items():
                cleaned_value = self.clean_value(key, value)
                if cleaned_value is not None:
                    cleaned_item[key] = cleaned_value
            return cleaned_item
        elif isinstance(item,list):
            cleaned_list = []
            for element in item:
                cleaned_element = self.clean_item(element)
                if cleaned_element:
                    cleaned_list.append(cleaned_element)
            return cleaned_list
        else:
            return item
    
    def clean_value(self, key, value):

        #the keys that need to be in float format
        float_keys = ['residence_charge','water','deposit','rent','living_area','sauna','deposit','right_of_occupancy_fee','other_area','total_area','other_heating','electric_heating','electricity','parking_space','tv_cable_tv']
        #the keys that need to be in int format
        int_keys = ['number_of_rooms','number_of_roommates','rental_number','renovation_year','construction_year','toiler_count','phone_connections','tv_connections','floor']
        #the keys that need to be in timestamp
        date_keys = ['inspection_done','vacancy']
        #the keys that are special and not devided
        special_str_keys = ['description_of_rental','more_information','special_terms','information_about_costs','further_information','additional_information_about_energy_certificate','name','maintenance','material_description','yard_description','room_description','other_info','past_renovation','driving_instructions','renovations','transportation','description']

        if isinstance(value, str):
            #float
            if key in float_keys:
                value = clean_number(value)

                match = re.search(r'(\d[\d,]*)', value)
                numeric_value = float(match.group().replace(',', '')) if match else None

                # Extract frequency information
                if '/w' in value or '/week' in value:
                    frequency = 'per_week'
                elif '/month'in value or '/m' in value:
                    frequency = 'per_month'
                elif '/year' in value or '/y' in value:
                    frequency = 'per_year'
                else:
                    frequency = None

                # Extract per_person information
                per_person = 'per_person' if '/person' in value else None

                # Update the cleaned_data dictionary
                cleaned_value = {
                    f"{key}_value": numeric_value,
                    f"{key}_frequency": frequency,
                    f"{key}_person": per_person
                }

                return cleaned_value
                        
            #int
            elif key in int_keys:
                try:
                    return int(re.search('\d+',value).group())
                except(ValueError,AttributeError):
                    return value
            #date timestamp
            elif key in date_keys:
                #convert to timestamp
                if value == "vacant immediately" or value == "on agreement":
                    return value
                else:
                    try:
                        date_formts = ["%m/%d/%y"]
                        for date_format in date_formts:
                            try:
                                value = datetime.strptime(value,date_format)
                                unix_timestamp = int(value.timestamp())
                                return unix_timestamp
                            except ValueError:
                                pass
                    except Exception as e:
                        return None
                    
            # convert into list
            elif key not in special_str_keys:

                try:
                    parts = value.split(',')
                    if len(parts) > 1:
                        self.list_dic[key] = None
                        return [part.strip() for part in parts]
                    else:
                        return value
                except AttributeError:
                    return value
            else:
                return value
            
        elif isinstance(value, dict):
            # Handle nested dictionaries (e.g., house_type or house data)
            cleaned_dict = {}
            for sub_key, sub_value in value.items():
                cleaned_sub_value = self.clean_value(sub_key, sub_value)
                if cleaned_sub_value is not None:
                    cleaned_dict[sub_key] = cleaned_sub_value
            return cleaned_dict
    
        elif isinstance(value, list):
            # Handle nested lists (e.g., list of house data)
            cleaned_list = []
            for element in value:
                cleaned_element = self.clean_value(None, element)
                if cleaned_element:
                    cleaned_list.append(cleaned_element)
            return cleaned_list
        
        else:
            return value
        