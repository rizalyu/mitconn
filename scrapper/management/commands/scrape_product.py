from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from master.models import Product, Category, Shop, ProductHistory

class Command(BaseCommand):
    help = 'Scrape a product'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('link', type=str, help='Product link')
        parser.add_argument('shop', type=str, help='Product owner')

    def handle(self, *args: Any, **options: Any):
        link = options['link']
        shop = options['shop']

        try:

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

            driver.get(link)

            product_name = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductName"]').text.title()
            product_desc = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDescriptionProduk"]').text

            temp = driver.find_elements(By.CSS_SELECTOR, '[data-testid="lblPDPInfoProduk"]')
            temp = temp[0]
            product_condition = temp.find_element(By.CLASS_NAME, 'main').text

            try:
                sold = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductSoldCounter"]').text.split(' ')[-1]
            except:
                sold = 0

            try:
                rating = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductRatingNumber"]').text
            except:
                rating = 0

            try:
                price = driver.find_element(By.CSS_SELECTOR, '[data-testid="lblPDPDetailProductPrice"]').text.strip('Rp').replace('.', '')
            except:
                price = 0

            try:   
                stock = driver.find_element(By.CSS_SELECTOR, '[data-testid="stock-label"]').find_element(By.TAG_NAME, 'b').text.split(' ')[-1]
            except:
                stock = 0

            breadcrumb_items = driver.find_elements(By.XPATH, "//li[@class='css-d5bnys']")
            scraped_category = breadcrumb_items[1].text


            category, created = Category.objects.get_or_create(name=scraped_category, defaults={
                'name': scraped_category
            })

            if created:
                self.stdout.write(f"Created {scraped_category} category")

            product, created = Product.objects.get_or_create(name=product_name, defaults={
                'owner': Shop.objects.get(name=shop),
                'category': category,
                'url': link,
                'name': product_name,
                'description': product_desc,
                'condition': product_condition
            })

            if created:
                self.stdout.write(f"Created {product_name}")

                ProductHistory.objects.create(product = product, price = price, sold = sold, rating = rating, stock = stock)

            if not created:
                self.stdout.write(f"{product_name} already exists in database!")
            

        except Exception as e:
            self.stderr.write(e)