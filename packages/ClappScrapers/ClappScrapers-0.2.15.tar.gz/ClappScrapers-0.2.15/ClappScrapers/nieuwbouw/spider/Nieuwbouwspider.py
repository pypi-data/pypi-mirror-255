import scrapy
from scrapy.http import TextResponse
import re
from scrapy.signalmanager import dispatcher
from scrapy import signals
import logging

logging.getLogger('scrapy').setLevel(logging.ERROR)


def clean_text(text):

    if text is None:

        return ''

    if text is not None:
                
        # Remove leading and trailing whitespaces, including newline characters
        cleaned_value = text.strip()

        # Replace consecutive newline characters with a single space
        cleaned_value = re.sub(r'\n+', ' ', cleaned_value)

        # Replace other unwanted characters
        cleaned_value = cleaned_value.replace("€", "").replace("\xa0", "").replace("  ","").replace("<td>","").replace("</td>","").replace('<td class="text-nowrap">',"").replace("m<sup>2</sup>","").replace("m<sup>3</sup>","").replace("-","").replace("<dd>","").replace("</dd>","").strip()


        # Use strip() to remove leading and trailing whitespace and newline characters
        return cleaned_value
    
def normalize_key (text):

    if text is None:
        return ''
    
    if text is not None:
        

        normalized_key = text.replace('(p.m.)','').replace('(s)','').strip()

        # Replace spaces with underscores
        normalized_key = normalized_key.replace(' ', '_').replace('.','').strip()
    
        # Remove special characters
        normalized_key = ''.join(char for char in normalized_key if char.isalnum() or char in ['_', '-'])

        # Decapitalize the key
        normalized_key = normalized_key.lower()

        return normalized_key


class NieuwbouwspiderSpider(scrapy.Spider):
    name = "Nieuwbouwspider"
    start_urls = ["https://www.nieuwbouw-in-amsterdam.nl/projecten/"]
    
    download_delay = 0.5  # 0.5 second delay between requests

    #set up a set for all the possible project keys
    all_possible_project_keys = set ()

    all_possible_house_type_keys = set()




    def parse(self, response):

            projects = response.css('a.card.card-project.card-project-list')


            #Extract project links (for spiders to crawl into)
        
            project_list = []

    
            for project in projects:

                project_info= {}

                project_link = project.css('a[href^="/project/"]::attr(href)').get()

                project_data = project.css('a.card.card-project.card-project-list').get()

                # Assuming project_data is a string containing  HTML

                project_data_bytes = project_data.encode('utf-8')

                project_data_html = TextResponse(url='dummyurl', body=project_data_bytes, encoding='utf-8')

                titles = project_data_html.css('svg[title]::attr(title)').getall()

                values = project_data_html.css('ul.list-inline li.list-inline-item span::text, ul.list-inline li.list-inline-item::text').getall()

                values = [clean_text(i) for i in values if i !=' ']

                titles = [normalize_key(i) for i in titles]

                count = 0
                for title in titles:
                    project_info[title] = values[count]
                    self.all_possible_project_keys.add(title)
                    count+=1

                if project_link:


                    yield response.follow(project_link, callback=self.parse_project_page,cb_kwargs={'projects':projects,'project':project,'project_info':project_info,'project_list':project_list})




    def parse_project_page(self, response, projects = None, project = None, project_list = list, project_info = None):

        # Extract information from the project


        #make the img_urls into a list instead of dict
        self.all_possible_project_keys.add("project_img_urls")
        project_imgs = response.css('img.img-fluid.w-100::attr(src)').getall()
        if project_imgs:
            project_info["project_img_urls"] = project_imgs


        labels = response.css('div.feature-label::text').getall()
        values = response.css('div.feature-value::text').getall()

        
        values = [clean_text(i) for i in values if i !=' ']
        labels = [normalize_key(i) for i in labels]

        if labels:
            count = 0
            for label in labels:
                 project_info[label] = values[count]
                 self.all_possible_project_keys.add(label)
                 count += 1
        
        self.all_possible_project_keys.add("over_dit_project") 

        project_description = response.css('section#project-beschrijving div.text-collapse p')
        if project_description :
             project_info ["over_dit_project"] = clean_text("".join(project_description.css('::text').getall()))


        self.all_possible_project_keys.add("project_source")   
        
        project_info['project_source'] = response.url

        project_info['stad'] = self.get_city_from_url(response.url)

        project_col = response.css('dl dt::text').getall()
        project_val = response.css('dl dd').getall()


        project_val = [clean_text(i) for i in project_val]

        #remove all the spaces inside the project_val 
        project_val = [i for i in project_val if i !='']

        project_col = [normalize_key(i) for i in project_col]

        #pair the project_col and project_val up in order
        count = 0
        for column_name in project_col:
            project_info[column_name] = project_val[count]
            self.all_possible_project_keys.add(column_name)
            count += 1

        #for project Type woningen make it into a list of strings in the pipeline 


        map_div = response.css('div#map')
        latitude = map_div.attrib['data-gemy']
        longitude = map_div.attrib['data-gemx']

        #separate the latitude and longitude
        project_info['locatie'] = { "latitude":latitude , "longitude":longitude }
        

        house_types = response.css('div.col-md-6.d-md-flex.d-lg-block')

        
        house_type_info_list = []

        project_info['house_types'] = house_type_info_list

        
        

        expected_house_types = len(house_types)

        found_house_types = False




        if house_types:
            

            house_type_links = house_types.css('a[href^="/type/"]::attr(href)').getall()
        

            for house_type_link in house_type_links:
                
                
                yield response.follow(house_type_link, callback=self.parse_house_type_page,cb_kwargs={'project_list':project_list,'project_info':project_info,'house_type_info_list':house_type_info_list,'expected_house_types':expected_house_types,'house_types':house_types})
                found_house_types = True

        #check if house_types were found
        if not found_house_types:
            yield project_info

            


#set up a check point for the situation if there is no sepicfic information for house type collections



    def parse_house_type_page(self,response, project = None, projects = None, project_list = list, project_info = None, house_type_info_list = list,expected_house_types = int, house_types = list):
        #Extract information from the collection

        house_type_data = response.css('table.table.table-responsive-md')

        #creat a list of house_info
        house_info_list = []
        #creat a lib called house_info
        house_info = {}

        self.all_possible_house_type_keys.update(['house_type_source','house_type_name'])
        house_type_info = {
                    'house_type_source':response.url,
                    'house_type_name':clean_text(response.css('h1.h2.card-title.font-weight-light.mb-4::text').get(default='')),
                }

        self.all_possible_house_type_keys.add("house_type_img_urls")
        house_type_imgs = response.css('img.img-fluid.w-100::attr(src)').getall()
        if house_type_imgs:
            house_type_info["house_type_img_urls"] = house_type_imgs

        self.all_possible_house_type_keys.add("over_dit_woningentype")
        house_type_description = response.css('div.col-md-10.text-md-center p')
        if house_type_description :
            house_type_info ["over_dit_woningentype"] = clean_text("".join(house_type_description.css('::text').getall()))   


        house_type_col = house_type_data.css('th::text').getall()
        house_type_val = house_type_data.css('td').getall()



        house_type_val = [clean_text(i) for i in house_type_val]
        #remove empty spaces in the outcome of 'house_types.css('td::text').getall()'

        house_type_val = [i for i in house_type_val if i !='']

        house_type_col = [normalize_key(i) for i in house_type_col]

        
         #pair the house_type_col and house_type_val up in order
        
        column_counts = {}  # To keep track of the counts for each column nameimport

        # Loop through the columns and values and add them to the dictionary
        for column_name, value in zip(house_type_col, house_type_val):
            # Check if the key already exists in the dictionary
            if column_name in house_type_info:
                # Increment the count for this column
                if column_name in column_counts:
                    column_counts[column_name] += 1
                else:
                    column_counts[column_name] = 1
                # Create a new key with a suffix
                new_key = f"{column_name}_{column_counts[column_name]}"
                house_type_info[new_key] = value
                self.all_possible_house_type_keys.add(new_key)
            else:
                # If the key doesn't exist, add it to the dictionary with the value
                house_type_info[column_name] = value
                self.all_possible_house_type_keys.add(column_name)




        house_type_info['houses'] = house_info_list

        house_type_info_list.append(house_type_info)
            

        # Extract information from the individuale unit   

        houses = response.css('table#tblBouwnummers tbody tr')

        #the number of expected houses found on  the page
        expected_houses = len(houses)
        

        if houses:

                        for house in houses:


                            house_info ={
                                 
                                'house_source':response.url,
                                'bouwnummer':clean_text(house.css('td')[0].get()) if len(house.css('td')) > 0 else None,
                                'prijs':clean_text(house.css('td')[1].get()) if len(house.css('td')) > 1 else None,
                                'prijs_conditie':'V.O.N',
                                'kaveloppervlak':'' if clean_text(house.css('td')[2].get()) == "" else clean_text(house.css('td')[2].get()) if len(house.css('td')) > 2 else None,
                                'woonoppervlak':clean_text(house.css('td')[3].get()) if len(house.css('td')) > 3 else None,
                                'slaapkamer':clean_text(house.css('td')[4].get()) if len(house.css('td')) > 4 else None,
                                'inhoud':clean_text(house.css('td')[5].get()) if len(house.css('td')) > 5 else None,
                                'status':clean_text(house.css('td')[6].get()) if len(house.css('td')) > 6 else None,  
                                        
                            }
                
                            house_info_list.append(house_info)
                        
                        if len(house_type_info_list) == expected_house_types:

                            if len(house_info_list) == expected_houses:                    


                                house_type_info_list.append(house_type_info)
                    

        
                                project_info['house_types'] = house_type_info_list

                                yield project_info

        elif len(house_type_info_list) == expected_house_types:
            
            yield project_info

    def get_city_from_url(self, url):
        # Use regex to extract the city name
        match = re.search(r'www\.nieuwbouw(?:-in)?-(\w+)', url)
        if match:
            return match.group(1)
        else:
            return None  # or any default value you prefer

    

    def closed(self, spider):
        # This method is called when the spider is finished

        # Print all possible project keys
        dispatcher.send(signal=signals.spider_closed, sender=spider, all_possible_project_keys=self.all_possible_project_keys,all_possible_house_type_keys=self.all_possible_house_type_keys)

