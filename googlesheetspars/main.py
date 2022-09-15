import time 
from loguru import logger
import quickstart 
from bs4 import BeautifulSoup 
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 

logger.add(r"Debug\debug{time}.log", format="{time} | {level} | {message}", level="DEBUG", rotation="10 KB", compression="zip")

@logger.catch
def get_data_with_selenium(url): 

    logger.info(f"Парсинг страницы по адресу: {url}")
    options = webdriver.ChromeOptions() 
    options.add_argument("Chrome/105.0.0.0 ") 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    try: 
        driver = webdriver.Chrome( 
        executable_path=r"googlesheetspars\chromedriver.exe", 
        options=options 
        ) 
        logger.info(f"Запуск драйвера с параметрами: user-agent: {options.arguments}; {options.experimental_options}")
        driver.get(url=url) 
        search_form = driver.find_element_by_tag_name('html') 
        for i in range(1,11): 
            search_form.send_keys(Keys.PAGE_DOWN) 
            time.sleep(2) 
        
        with open("index_selenium.html", "w", encoding='utf-8') as file: 
            file.write(driver.page_source) 
        logger.info(f"Запись html страницы в {file.name} прошла успешно")
        driver.close() 
        driver.quit() 
    except Exception as ex: 
        logger.error(ex) 

    try:
        with open("index_selenium.html", encoding='utf-8') as file: 
            src = file.read()
            logger.info(f"Чтение файла {file.name} прошло успешно")
    except FileNotFoundError as ex:
            logger.error(ex) 
    
    soup = BeautifulSoup(src, "lxml") 
    pizza ={} 
    pizza_descriptblock = soup.find_all("div", class_="sc-1g5me89-12 lkFkIu") 
    
    for item in pizza_descriptblock: 
        try: 
            pizza[item.find("p",class_="sc-1g5me89-19 crKlJl").text] = item.find("div",class_="sc-1g5me89-16 jRHKei").text 
        except AttributeError  as ex: 
            pizza[item.find("p",class_="sc-1g5me89-19 crKlJl").text] = "composite" 
            logger.warning(ex)
    try:
        gs = quickstart.GoogleSheet() 
        logger.info("Создан ресурс для взаимодействия с Google API")
    except Exception as ex:
        logger.error(ex)

    pizza_range = f'Test List!A1:B{len(pizza)}' 
    
    
    pizza_values = [] 
    for value, key in pizza.items(): 
        pizza_values.append([value,key]) 
    try:
        gs.updateRangeValues(pizza_range, pizza_values) 
        logger.info(f"Обновлено: {pizza_range}")
    except Exception as ex:
        logger.error(ex)


def main():
    get_data_with_selenium("https://dominospizza.ru/") 
    
 
if __name__== '__main__': 
    main()