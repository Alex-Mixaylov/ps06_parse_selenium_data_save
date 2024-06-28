from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import csv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ElectricalApplianceParser:
    def __init__(self):
        # Настройка опций для запуска браузера в фоновом режиме
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск без открытия окна браузера
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Указание пути к chromedriver
        service = ChromeService(executable_path=r"C:\Windows\chromedriver.exe")

        # Инициализация веб-драйвера
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.urls = [
            "https://www.divan.ru/category/svet",
            "https://www.divan.ru/category/svet/page-2",
            "https://www.divan.ru/category/svet/page-3",
            "https://www.divan.ru/category/svet/page-4",
            "https://www.divan.ru/category/svet/page-5",
            "https://www.divan.ru/category/svet/page-6",
            "https://www.divan.ru/category/svet/page-7"
        ]
        self.light_list = []

    def parse(self):
        for url in self.urls:
            logging.info(f'Парсинг страницы: {url}')
            self.driver.get(url)

            # Парсинг товаров на текущей странице
            lights = self.driver.find_elements(By.CSS_SELECTOR, 'div._Ud0k')
            for light in lights:
                try:
                    name = light.find_element(By.CSS_SELECTOR, 'div.lsooF span').text
                    price = light.find_element(By.CSS_SELECTOR, 'div.pY3d2 span.ui-LD-ZU.KIkOH').text
                except Exception as e:
                    logging.error(f'Ошибка при получении наименования или цены: {e}')
                    continue

                try:
                    price_old = light.find_element(By.CSS_SELECTOR, 'div.pY3d2 span.ui-LD-ZU.ui-SVNym.bSEDs').text
                except Exception as e:
                    price_old = '0'
                    logging.error(f'Ошибка при получении старой цены: {e}')

                try:
                    sale = light.find_element(By.CSS_SELECTOR, 'div.pY3d2 div.ui-JhLQ7').text
                except Exception as e:
                    sale = 'нет скидки'
                    logging.error(f'Ошибка при получении скидки: {e}')

                url = light.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                item = {
                    'name': name,
                    'price': price,
                    'price_old': price_old,
                    'sale': sale,
                    'url': url
                }
                if item not in self.light_list:  # Избежание дублирования
                    self.light_list.append(item)

            logging.info(f'На странице {url} спарсено товаров: {len(lights)}')

    def save_to_csv(self):
        # Сохранение данных в файл CSV
        keys = self.light_list[0].keys()
        with open('lights.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.light_list)
        logging.info('Данные успешно сохранены в lights.csv')
        logging.info(f'Общее количество спарсенных товаров: {len(self.light_list)}')

    def run(self):
        # Запуск процесса парсинга и сохранения данных
        self.parse()
        self.save_to_csv()
        self.driver.quit()


if __name__ == "__main__":
    parser = ElectricalApplianceParser()
    parser.run()
