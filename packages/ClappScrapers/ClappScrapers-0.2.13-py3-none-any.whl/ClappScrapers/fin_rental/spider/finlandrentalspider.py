import scrapy
from scrapy.exceptions import CloseSpider
import re
import time
from urllib.parse import urljoin



def clean_text(text):

    if text is None:

        return '-'

    if text is not None:

        cleaned_value = re.sub(r'<[^>]*>', '', text)
                
        # Remove leading and trailing whitespaces, including newline characters
        cleaned_value = cleaned_value.strip()

        # Replace consecutive newline characters with a single space
        cleaned_value = re.sub(r'\n+', ' ', cleaned_value)

        # Replace other unwanted characters
        cleaned_value = cleaned_value.replace("\xa0", "").replace("  ","").replace("m<sup>2</sup>","").replace("m<sup>3</sup>","").replace("\r","").replace("\t","").strip()


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

        normalized_key = normalized_key.replace('__',"_")

        # Decapitalize the key
        normalized_key = normalized_key.lower()

        return normalized_key



class finlandrentalspiderSpider(scrapy.Spider):
    
    name = "finlandrentalspider"
    start_urls = ["https://www.vuokraovi.com/vuokra-asunnot?locale=en&page=1&pagetype="]
    base_url = "https://www.vuokraovi.com/vuokra-asunnot?locale=en&page={}&pageType="

    custom_settings = {
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
        'RETRY_TIMES': 5,
        'RETRY_PRIORITY_ADJUST': -1,        
        'DOWNLOAD_DELAY' : 2,  # 2 second delay between requests
        'HTTPERROR_ALLOW_ALL' : True,
    }


    all_possible_property_keys = set()

    max_retries = 3  # Set the maximum number of retries

    retry_counter = 0


    def parse(self, response):

                    
        property_list = []

        #initialize a set for all the possible keys in project_info to keep the amount of the keys for each dict project_info the same

        #Find all the properties
        properties = response.css('div.list-item-container div.row.top-row a.list-item-link[onclick^="setScrollPositionInCookie()"]')

        last_button = response.css('a.list-pager-button').getall()[-1]
        alt_content = scrapy.Selector(text=last_button).css('::attr(alt)').get()

        page_match = re.search(r'page=(\d+)', response.url)

        current_page = int(page_match.group(1))

        # Calculate the next page number with an increment of 1
        next_page_number = current_page + 1

        # Construct the next page URL
        next_page_link = self.base_url.format(next_page_number)
        
        if alt_content == 'Previous':

            raise CloseSpider("Reach the last page")

        if not properties:

            if self.retry_counter >= self.max_retries:

                self.logger.warning("Max retries reached, next page...")
                
                self.retry_counter = 0

                yield scrapy.Request(url=next_page_link, callback=self.parse)

            else:
                
                self.retry_counter += 1

                self.logger.warning("No properties found, waiting and retrying on the same page... (Retry {}/{}))".format(self.retry_counter, self.max_retries))

                time.sleep(0.5)

                # Make a request to the next page
                yield scrapy.Request(url=response.url, callback=self.parse)

        
        if properties:

            self.retry_counter = 0
        
        for property in properties :

            property_info= {}

            property_list.append(property_info)

            #Extract project links (for spiders to crawl into)

            property_link = property.css('a ::attr(href)').get()

            english_property_url = urljoin(property_link, '?locale=en')

                            
            if property_link:
                    
                yield scrapy.Request(url='https://www.vuokraovi.com' + english_property_url, callback=self.parse_property_page,cb_kwargs={'property_info':property_info})        
        
        else:

            yield scrapy.Request(url=next_page_link, callback=self.parse)
        

    
    def parse_property_page(self,response, property_info= None):



        try:


            property_info['source'] = response.url

            property_info['description_of_rental'] = clean_text(''.join(response.css('div#itempageDescription p::text').getall()))

            property_info['location'] = clean_text(' '.join(response.css('div.panel-body table tbody tr td a::text, div.panel-body table tbody tr td span::text').getall()[0:4]))


            property_columns = response.css('div.panel-body table tbody th::text').getall()[1:-1]
            property_columns = [normalize_key(i) for i in property_columns]

            self.all_possible_property_keys.update(property_columns)

            property_values = response.xpath('//div[@class="panel-body"]//table//tbody//td').getall()[1:-1]
            property_values = [clean_text(i) for i in property_values]
            property_values = [(i) for i in property_values if i != '' and i != ',']


            count = 0
            for column in property_columns:
                property_info[column] = property_values[count]
                count += 1

            property_info['information_url'] = response.css('td ul li a::attr(href)').getall()

            if property_info['description_of_rental'] == "":

                if not hasattr(self,'retry_count_property_page'):

                    self.retry_count_property_page = 0

                if self.retry_count_property_page < 2:

                    self.retry_count_property_page += 1
                    self.logger.warning("Page not loaded while parsing property page. Retrying the same page(Retry{}/2)...".format(self.retry_count_property_page))

                    yield scrapy.Request(url=response.url, callback=self.parse_property_page, cb_kwargs={'property_info':property_info})
                else:
                    self.retry_count_property_page = 0
                    self.logger.warning("Max retries reached for property page, moving on to the next property...")
                    return
            

            yield property_info

        except (IndexError, ValueError):

            # Catch IndexError and retry the same page
            if not hasattr(self, 'retry_counter_property_page'):
                self.retry_counter_property_page = 0

            if self.retry_counter_property_page < 2:
                self.retry_counter_property_page += 1
                self.logger.warning("IndexError while parsing property page. Retrying the same page (Retry {}/2)...".format(self.retry_counter_property_page))
                yield scrapy.Request(url=response.url, callback=self.parse_property_page, cb_kwargs={'property_info': property_info})
            else:
                self.retry_counter_property_page = 0
                self.logger.warning("Max retries reached for property page, moving on to the next property...")
                return
        




    def closed(self, reason):
        # This method is called when the spider is finished

        # Print all possible property keys
        self.log("All possible property keys:")
        for key in self.all_possible_property_keys:
            self.log(key)