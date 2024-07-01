from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options  import Options
from webdriver_manager.chrome import ChromeDriverManager
from master.models import Product, ProductHistory

class Command(BaseCommand):
    help = "Scrape Product History"

    def handle(self, *args: Any, **options: Any):

        for product in Product.objects.all():

            try:
                driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

                driver.get(product.url)

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

                ProductHistory.objects.create(product = product, price = price, sold = sold, rating = rating, stock = stock)
                self.stdout.write(f"Created Product History for {product.name}")

            except Exception as e:
                print(e)