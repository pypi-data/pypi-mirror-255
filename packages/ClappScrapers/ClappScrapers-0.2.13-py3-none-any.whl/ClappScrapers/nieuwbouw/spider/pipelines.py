# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
from scrapy import signals
from scrapy.signalmanager import dispatcher


def clean_number(number):
    
    if number is None:
          return ""

         
    cleaned_number = number.replace("tot"," ").replace(".","").replace(",",".").replace("vanaf","")

    if cleaned_number.endswith("m"):
        cleaned_number = cleaned_number[:-1]
    
    return cleaned_number

class MergedDataPipeline:
    def __init__(self):
        self.raw_data = []
        self.cleaned_data = []
        self.list_dic = {}

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('project_source'):
            # Process raw data
            self.raw_data.append(adapter.asdict())

            # Process cleaned data
            cleaned_item = self.clean_item(item)
            self.cleaned_data.append(cleaned_item)

        return item

    def close_spider(self, spider):

        # Convert values to list for keys in list_dic
        for key in self.list_dic:
            for cleaned_item in self.cleaned_data:
                self.convert_to_list(cleaned_item, key)

        # Process data
        spider.log("pipeline Closing spider and sending custom_closed_signal...")
        dispatcher.send(signal=signals.spider_closed, sender=spider, cleaned_data=self.cleaned_data, raw_data=self.raw_data,list_dic=self.list_dic)

        # Call the pipelines_finished function to send both raw_data and cleaned_data
        #pipelines_finished(spider, self.raw_data, self.cleaned_data)

    def convert_to_list(self, cleaned_item, key):
        # Recursive function to convert values to list for a specific key
        if isinstance(cleaned_item, dict):
            for sub_key, sub_value in cleaned_item.items():
                if sub_key == key and sub_key in self.list_dic:
                    cleaned_item[sub_key] = [sub_value] if not isinstance(sub_value, list) else sub_value
                elif isinstance(sub_value, (dict, list)):
                    self.convert_to_list(sub_value, key)
        elif isinstance(cleaned_item, list):
            for element in cleaned_item:
                self.convert_to_list(element, key)


    def clean_item(self, item):
        if isinstance(item, dict):
            cleaned_item = {}
            for key, value in item.items():
                cleaned_value = self.clean_value(key, value)
                if cleaned_value is not None:
                    cleaned_item[key] = cleaned_value
            return cleaned_item
        elif isinstance(item, list):
            cleaned_list = []
            for element in item:
                cleaned_element = self.clean_item(element)
                if cleaned_element:
                    cleaned_list.append(cleaned_element)
            return cleaned_list
        else:
            return item
        

    def clean_value(self, key, value):

        
        if isinstance(value, str):
            if key in ['woonoppervlak','kaveloppervlak','woonoppervlakte','inhoud','kavel']:
                parts = clean_number(value).split()

                if len(parts) == 2:
                    min_area = float(parts[0])
                    max_area = float(parts[1])
                    return {"min_area": min_area, "max_area": max_area}
                if len(parts) == 1:
                    area = float(parts[0])

                    return area
                else:
                    return None
                
            if key in ['prijs', 'huurprijs','prijs_vanaf']:
                parts = clean_number(value).split()

                if len(parts) == 2:
                    min_price = float(parts[0])
                    max_price = float(parts[1])
                    return {"min_price": min_price, "max_price": max_price}
                if len(parts) == 1:
                    price = float(parts[0])
                    return price
                else:
                    return None
                
            if key in ['latitude','longitude']:

                cor = float(value)
                return cor

                
            elif key in ['aantal_koopwoningen', 'aantal_woningtypes', 'huurwoningen', 'aantal_slaapkamer', 'koopwoningen','slaapkamer','aantal_huurwoningen']:

                parts = clean_number(value).split()

                if len(parts) == 2:
                    min_value = int(parts[0])
                    max_value = int(parts[1])
                    return {"min": min_value, "max": max_value}
                if len(parts) == 1:
                    value = int(parts[0])
                    return value
                else:
                    return None
                
            elif value == "":
                return None
            
            elif key not in ['over_dit_project','over_dit_woningentype','project']:
                
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