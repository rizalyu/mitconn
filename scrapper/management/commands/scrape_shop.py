from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options  import Options
from webdriver_manager.chrome import ChromeDriverManager
from master.models import Shop, ShopHistory

class Command(BaseCommand):
    help = 'Scrape a product'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('link', type=str, help='Product link')

    def handle(self, *args: Any, **options: Any):
        link = options['link']

        try:

            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

            driver.get(link)

            shop_name = driver.find_element(By.CSS_SELECTOR, '[data-testid="shopNameHeader"]').text
            shop_location = driver.find_element(By.CSS_SELECTOR, '[data-testid="shopLocationHeader"]').text
            shop_rating = driver.find_element(By.CLASS_NAME, 'css-1hczjm3-unf-heading').text

            shop, created = Shop.objects.get_or_create(name = shop_name, defaults={
                'name': shop_name,
                'location': shop_location
            })

            if created:
                self.stdout.write(f"Created {shop_name}")

                ShopHistory.objects.create(
                    shop = shop,
                    rating = shop_rating
                )

        except Exception as e:
            self.stderr.write(e)