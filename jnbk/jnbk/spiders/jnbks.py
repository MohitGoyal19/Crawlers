# -*- coding: utf-8 -*-
import scrapy


class JnbkSpider(scrapy.Spider):
    name = 'jnbk'
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    def start_requests(self):
        url = 'http://www.jnbk-brakes.com/catalogue/cars'
        
        yield scrapy.Request(url=url, callback=self.get_makes, dont_filter=True)

    
    def get_makes(self, response):
        makes = response.css('#selBrand option::attr(value)').getall()

        for make in makes:
            url = f'http://www.jnbk-brakes.com/application/get_application_models/{make}/1/0'
            
            yield scrapy.Request(url=url, headers=self.headers, callback=self.get_models, dont_filter=True)


    def get_models(self, response):
        models = response.css('option::attr(value)').getall()

        for model in models:
            url = 'http://www.jnbk-brakes.com/application/get_applications/' + model.strip('\\').strip('"').strip('\\') + '/1'

            yield scrapy.Request(url=url, headers=self.headers, callback=self.get_brakes, dont_filter=True)

    
    def get_brakes(self, response):
        brakes = response.css('table a::attr(href)').getall()

        for brake in brakes:
            yield scrapy.Request(url=brake, headers=self.headers, callback=self.parse, dont_filter=True)


    def parse(self, response):
        for image in response.css('img'):
            if image.attrib['alt'].strip() == response.url.split('/')[-1]:
                img = image.attrib['src']
        
        specifications = ' ^ '.join([title.strip().replace('\n', ' ') + '|' + field.strip().replace('\n', ' ') for title, field in zip(response.css('.detail__specification .param-title ::text').getall(), response.css('.detail__specification .param-field ::text').getall())])
        alternatives = ' ^ '.join([alt.strip().replace('\n', ' ') for alt in response.css('.detail__plate a ::text').getall()])
        cross_refs = ' ^ '.join([ref.strip().replace('\n', ' ') for ref in response.css('.flex-wrap .str ::text').getall()]).strip().strip('^').replace('^  ^  ^', '^').replace('^  ^', '|')

        for model in range(len(response.css('.model-title h3 a ::text').getall())):
            (make, car_model) = response.css('.model-title h3 a ::text').getall()[model].strip().split('»')
            rows = response.css('.model-body')[model].css('tr ::text').getall()

            for row in rows:
                front_rotor = ' ^ '.join([rotor.strip() for rotor in response.css('td')[4].css('a ::text').getall()] + [rotor.strip() for rotor in response.css('td')[4].css('span ::text').getall()])
                front_brake = ' ^ '.join([rotor.strip() for rotor in response.css('td')[5].css('a ::text').getall()]  + [rotor.strip() for rotor in response.css('td')[5].css('span ::text').getall()])
                rear_rotor = ' ^ '.join([rotor.strip() for rotor in response.css('td')[6].css('a ::text').getall()] + [rotor.strip() for rotor in response.css('td')[6].css('span ::text').getall()])
                rear_brake = ' ^ '.join([rotor.strip() for rotor in response.css('td')[7].css('a ::text').getall()] + [rotor.strip() for rotor in response.css('td')[7].css('span ::text').getall()])
                
                year_start, year_end = (2000+int(response.css('.tdYear ::text').get().strip().split('~')[0].split('.')[1]), 2000+int(response.css('.tdYear ::text').get().strip().split('~')[1].split('.')[1])) if response.css('.tdYear ::text').get().strip().split('~')[1] else (2000+int(response.css('.tdYear ::text').get().strip().split('~')[0].split('.')[1]), 2020)
                for year in range(year_start, year_end+1):
                    yield{
                        'Break Id': response.url.split('/')[-1],
                        'Maker': make.strip(),
                        'Model': car_model.strip(),
                        'Year': year,
                        'Engine Vol': response.css('td ::text').getall()[1].strip(),
                        'Engine No': response.css('td ::text').getall()[2].strip(),
                        'Body': response.css('td ::text').getall()[3].strip(),
                        'Front Rotor': front_rotor.strip() if front_rotor else response.css('td ::text').getall()[4].strip(),
                        'Front Brake': front_brake.strip() if front_brake else response.css('td ::text').getall()[5].strip(),
                        'Rear Rotor': rear_rotor.strip() if rear_rotor else response.css('td ::text').getall()[6].strip(),
                        'Rear Brake': rear_brake.strip() if rear_brake else response.css('td ::text').getall()[7].strip(),
                        'Parking Shoe': response.css('td ::text').getall()[8].strip(),
                        'Specifications': specifications,
                        'Alternatives': alternatives,
                        'Cross References': cross_refs,
                        'Product Url': response.url,
                        'Image Url': img
                    }
