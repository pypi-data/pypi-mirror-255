import scrapy
from scrapy.exceptions import CloseSpider
import re
import time

def clean_text(text):

    if text is None:

        return '-'

    if text is not None:
                
        # Remove leading and trailing whitespaces, including newline characters
        cleaned_value = text.strip()

        # Replace consecutive newline characters with a single space
        cleaned_value = re.sub(r'\n+', ' ', cleaned_value)

        # Replace other unwanted characters
        cleaned_value = cleaned_value.replace("\u2022", "").replace("\u2013", "").replace("\u2028", "").replace("\u0000", "").replace("\u00A0", "").strip()

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



class boligportalspiderSpider(scrapy.Spider):
    name = "boligportalspider"
    start_urls = ["https://www.boligportal.dk/en/rental-properties/?offset=0"]
    base_url = "https://www.boligportal.dk/en/rental-properties/?offset={}"

    all_possible_property_keys = set()

    max_retries = 3  # Set the maximum number of retries

    retry_counter = 0


    def parse(self, response):

        #initialize a set for all the possible keys in project_info to keep the amount of the keys for each dict project_info the same

        #Find all the properties
        properties = response.css('div.css-vpsg7t div.temporaryFlexColumnClassName.css-mom5ju div.css-1hh4zdq div.css-1gtq2pq div.temporaryFlexColumnClassName.css-1a08xid')

        last_button = response.css('button.temporaryButtonClassname.css-12fwxlp')[-1]

        is_disabled = last_button.css('::attr(disabled)').get() is not None

        # Extract the current page number from the URL
        current_page = int(response.url.split("offset=")[1])

        # Calculate the next page number with an increment of 18
        next_page_number = current_page + 18

        # Construct the next page URL
        next_page_url = self.base_url.format(next_page_number)

        if is_disabled:

            raise CloseSpider("Reach the last page")


        if not properties:

            if self.retry_counter >= self.max_retries:

                self.logger.warning("Max retries reached, next page...")
                
                self.retry_counter = 0

                yield scrapy.Request(url=next_page_url, callback=self.parse)

            else:

                self.retry_counter += 1

                self.logger.warning("No properties found, waiting and retrying on the same page... (Retry {}/{}))".format(self.retry_counter, self.max_retries))

                time.sleep(0.5)

                yield scrapy.Request(url=response.url, callback=self.parse)

        if properties:

            self.retry_counter = 0    
    
        for property in properties :

            property_info= {}

            #Extract project links (for spiders to crawl into)

            property_link = property.css('div.css-1e7fg19 a ::attr(href)').get()

                        
            if property_link:
                
                yield scrapy.Request(url='https://www.boligportal.dk' + property_link, callback=self.parse_property_page,cb_kwargs={'property_info':property_info})

        
        else:

            # Make a request to the next page
            yield scrapy.Request(next_page_url, callback=self.parse)

    
    def parse_property_page(self,response, property_info= None, retry_attempt=0):


        property_info['source'] = response.url

        property_info['description'] = clean_text(response.css('div.css-1oj64sa div.css-1f7mpex::text').get())

        property_info['address'] = response.css('div.css-v49nss::text').getall()[1]
        
        #parse keys 
        about_property_columns = response.css('div.css-11rix5h section.css-y8cidf:nth-child(1) div.temporaryFlexColumnClassName.css-etn5cp span.css-arxwps::text').getall()[:16]
        #normalize keys
        about_property_columns = [normalize_key (i) for i in about_property_columns]

        property_values = response.css('div.css-11rix5h section.css-y8cidf:nth-child(1) div.temporaryFlexColumnClassName.css-etn5cp span.css-1h46kg2::text').getall()[:16]


        count = 0
        for column in about_property_columns:
            property_info[column] = property_values[count]
            count += 1

        #parse energy_label info
        property_info['energy_label'] = ()
        if response.css('div[tabindex="-1"][data-state="closed"] img.css-rdsunt::attr(src)').get():

            property_info['energy_label'] = response.css('div[tabindex="-1"][data-state="closed"] img.css-rdsunt::attr(src)').get().split("/")[-1].split("_")[0]

        else:
            property_info['energy_label'] = '-'

        #parse the keys
        about_rental_columns = response.css('div.css-11rix5h section.css-y8cidf:nth-child(2) div.temporaryFlexColumnClassName.css-etn5cp span.css-arxwps::text').getall()

        #normalize keys
        about_rental_columns = [normalize_key (i) for i in about_rental_columns]

        rental_values = response.css('div.css-11rix5h section.css-y8cidf:nth-child(2) div.temporaryFlexColumnClassName.css-etn5cp span.css-1h46kg2::text').getall()

        count = 0
        for column in about_rental_columns:
            property_info[column] = rental_values[count]
            count += 1



        if not property_info and retry_attempt < 1 :
            # Raise an exception to trigger the errback function
            raise Exception("Conditions not met")

        yield property_info

def retry_request(self, failure):
    if failure.check(Exception) and "Retry request" in str(failure.value):
        retry_attempt = failure.request.cb_kwargs.get('retry_attempt', 0)
    # Handle retries here
        if failure.check(Exception):
            # Reload the same page and retry the request
            url = failure.request.url
            self.logger.warning("Retrying the request for URL: %s (Retry %d)", url,retry_attempt + 1)
            yield scrapy.Request(
                url=url,
                callback=self.parse_property_page,
                cb_kwargs={'property_info': failure.request.cb_kwargs['property_info'],'retry_attempt': retry_attempt + 1},
                errback=self.retry_request  # Continue retrying
            )


