from time import sleep
import os

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

MAIN_URL = r'https://zullu.com.ua/product_list'


def connect(url = MAIN_URL):
    options = webdriver.ChromeOptions()

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")

    driver = Chrome(options=options)

    driver.set_window_size(1920, 1080)
    driver.get(url)

    return driver


def get_all_node_links(driver):
    sleep(1)
    nodes = driver.find_element_by_class_name('b-product-groups-gallery').find_elements_by_tag_name('li')

    links = []
    for node in nodes:
        links.append(node.find_element_by_class_name('b-product-groups-gallery__image-link').get_attribute('href'))

    return links


def save_image(code, num, link):
    if os.path.isfile(f'images/{code}/img_{num}.png'): return

    driver = connect(link)

    with open(f'images/{code}/img_{num}.png', 'wb') as file:
        file.write(driver.find_element_by_tag_name('img').screenshot_as_png)

    driver.close()


def save_item_images(code, driver):
    if not os.path.isdir('images'): os.mkdir('images')
    if not os.path.isdir(f'images/{code}'): os.mkdir(f'images/{code}')

    driver.find_element_by_class_name('b-product-image__img').click()

    w_time = 0
    while True:
        try:
            num = int(driver.find_element_by_class_name('b-images-view__header').text.split()[-1])
            break
        except NoSuchElementException:
            w_time+=1
            sleep(0.001)
            if w_time > 2000: break
            continue

    save_image(code, 1, driver.find_element_by_class_name('b-images-view__photo').get_attribute('src'))
    num = -1
    while True:
        w_time = 0
        while True:
            try:
                driver.find_element_by_class_name('b-images-view__button_direction_right').click()
                break
            except NoSuchElementException:
                w_time+=1
                sleep(0.001)
                if w_time > 2000: 
                    num = 1
                    break
                continue
        
        if num == 1: break

        num = int(driver.find_element_by_class_name('b-images-view__header').text.split()[-1])

        save_image(code, num, driver.find_element_by_class_name('b-images-view__photo').get_attribute('src'))


def get_item_data(link):
    driver = connect(link)
    sleep(1)
    
    name = driver.find_element_by_class_name('b-title_type_product').find_element_by_tag_name('span').text
    print(f'Load data - [{name}]')

    article = driver.find_element_by_class_name('b-product-data__item_type_sku').find_element_by_tag_name('span').text

    path_items = driver.find_element_by_class_name('breadcrumbs-1WtpdcnpBj').find_elements_by_class_name('link-2YsvoQ35xR')[1:]
    path = ''
    for item in path_items:
        path += item.text + '/'
    
    description = driver.find_element_by_class_name('b-user-content').text.replace('\n', ' ').replace('\t', ' ')

    driver.find_elements_by_class_name('b-tab-control__item')[1].click()
    attribute_cells = driver.find_element_by_tag_name('tbody').find_elements_by_class_name('b-product-info__cell')
    attribute = ''
    for i in range(0, len(attribute_cells), 2):
        attribute += f'{attribute_cells[i].text}:{attribute_cells[i+1].text}, '

    driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
    sleep(1)

    while True:
        w_time = 0
        try:
            header_class = driver.find_element_by_class_name('b-carousel__button_type_next').get_attribute('class').split()[-1]
            break
        except NoSuchElementException:
            w_time+=1
            sleep(0.001)
            if w_time > 2000: break
            continue

    referral = set()
    if header_class == 'b-carousel__button_state_active':
        while header_class == 'b-carousel__button_state_active':
            referral_items = driver.find_elements_by_class_name('b-carousel__holder')[0].find_elements_by_class_name('b-carousel__title')

            for item in referral_items:
                referral.add(item.text)

            w_time = 0
            while True:
                try:
                    header_class = driver.find_element_by_class_name('b-carousel__button_type_next').get_attribute('class').split()[-1]
                    driver.find_element_by_class_name('b-carousel__button_type_next').click()
                    break
                except NoSuchElementException:
                    w_time+=1
                    sleep(0.001)
                    if w_time > 2000: break
                    continue
                except ElementNotInteractableException:
                    w_time+=1
                    sleep(0.001)
                    if w_time > 2000: break
                    continue
                except ElementClickInterceptedException:
                    w_time+=1
                    sleep(0.001)
                    if w_time > 2000: break
                    continue
    else:
        referral_items = driver.find_elements_by_class_name('b-carousel__holder')[0].find_elements_by_class_name('b-carousel__title')
        for item in referral_items:
            referral.add(item.text)

    try:
        referral.remove('')
    except KeyError:
        pass

    item_data = {
        'name'          : name,
        'price'         : driver.find_element_by_class_name('b-product-cost__price').text,
        'available'     : driver.find_element_by_class_name('b-product-data__item_type_available').text,
        'article'       : article,
        'path'          : path,
        'description'   : description,
        'attribute'     : attribute,
        'link'          : link,
        'referral'      : referral
    }

    print('Saving images...')
    driver.find_element_by_tag_name('html').send_keys(Keys.UP)
    save_item_images(article, driver)

    driver.close()

    return item_data


def load_all_items(link):
    driver = connect(link)

    items_on_page = driver.find_element_by_class_name('b-product-gallery').find_elements_by_tag_name('li')
    print(f'Summary [{len(items_on_page)}] items on current page')

    data = []
    for item in items_on_page:
        print('-'*100)
        item_link = item.find_element_by_class_name('b-product-gallery__image-link').get_attribute('href')
        data.append(get_item_data(item_link))
        
        break ### Тестовое ограничение на 1 элемент [!!!]

    driver.close()

    return data

def delete_wrong_symbols(str):
    return str.encode(encoding="cp1251", errors="ignore").decode(encoding="cp1251", errors="ignore")

def save_data(file, data):
    for item in data:
        buff = ''
        for ref in item['referral']:
            buff += ref + '\t'

        file.write( delete_wrong_symbols(item['name'])        + '\t' +
                    delete_wrong_symbols(item['price'])       + '\t' +
                    delete_wrong_symbols(item['available'])   + '\t' +
                    delete_wrong_symbols(item['article'])     + '\t' +
                    delete_wrong_symbols(item['path'])        + '\t' +
                    delete_wrong_symbols(item['description']) + '\t' +
                    delete_wrong_symbols(item['attribute'])   + '\t' +
                    delete_wrong_symbols(item['link'])        + '\t' +
                    delete_wrong_symbols(buff)                + '\n')


def main():
    print('Power on')
    print('Connecting to website...')
    driver = connect()
    
    print('Load all catalogs...')
    links = get_all_node_links(driver) 

    with open('data.xls','w',encoding='cp1251',newline='') as file:
        file.write('Наименование\tЦена\tНаличие\tАртикул\tПуть\tОписание\tХарактеристики\tСсылка\tРекомендации\n')
        for link in links:
            print('='*100)
            items_data = load_all_items(link)

            print('Saving data into table...')
            save_data(file, items_data)
            
            #break ### Тестовое ограничение на 1 элемент [!!!]

    print('Power off')
    

if __name__ == '__main__':
    main()
