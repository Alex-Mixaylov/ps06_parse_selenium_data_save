from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ElectricalApplianceParser:
    def __init__(self):
        # Инициализация веб-драйвера и начальных параметров
        self.driver = webdriver.Chrome()
        self.url = "https://www.divan.ru/category/svet"
        self.light_list = []

    def parse(self):
        # Открытие начальной страницы
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 30)
        page_number = 1

        while True:
            logging.info(f'Парсинг страницы номер {page_number}')

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

            logging.info(f'На странице номер {page_number} спарсено товаров: {len(lights)}')

            # Прокрутка страницы вниз для подгрузки новых товаров
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)  # ожидание загрузки страницы

            # Ожидание загрузки новых элементов
            try:
                new_light_count = wait.until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div._Ud0k')) > len(lights))
            except Exception as e:
                logging.info('Новые товары не найдены, завершение парсинга')
                break

            page_number += 1

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
