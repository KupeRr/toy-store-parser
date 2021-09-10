from time import sleep

from selenium.webdriver import Chrome
from selenium import webdriver

MAIN_URL = r'https://zullu.com.ua/product_list'

def connect():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = Chrome(options=options)
    driver.get(MAIN_URL)
    return driver

def get_all_node_links(driver):
    sleep(1)
    nodes = driver.find_element_by_class_name('b-product-groups-gallery').find_elements_by_tag_name('li')

    links = []
    for node in nodes:
        links.append(node.find_element_by_class_name('b-product-groups-gallery__image-link').get_attribute('href'))

    return links

def get_item_data(driver, link):
    driver.get(link)

    path_items = driver.find_element_by_class_name('breadcrumbs-1WtpdcnpBj').find_elements_by_class_name('link-2YsvoQ35xR')[1:]

    path = ''
    for item in path_items:
        path += item.text + '/'

    descr_text_lines = driver.find_element_by_class_name('b-user-content').find_elements_by_tag_name('p')

    description = ''
    for line in descr_text_lines:
        description += line.text + ' '

    driver.find_elements_by_class_name('b-tab-control__item')[1].click()
    attribute_cells = driver.find_element_by_tag_name('tbody').find_elements_by_class_name('b-product-info__cell')

    attribute = ''
    for i in range(0, len(attribute_cells), 2):
        attribute += f'{attribute_cells[i].text}:{attribute_cells[i+1].text} '

    return {
        'name'          : driver.find_element_by_class_name('b-title_type_product').find_element_by_tag_name('span').text,
        'price'         : driver.find_element_by_class_name('b-product-cost__price').find_element_by_tag_name('span').text,
        'available'     : driver.find_element_by_class_name('b-product-data__item_type_available').text,
        'article'       : driver.find_element_by_class_name('b-product-data__item_type_sku').find_element_by_tag_name('span').text,
        'path'          : path,
        'description'   : description,
        'attribute'     : attribute,
        'link'          : link,
    }

def load_all_items(driver, link):
    driver.get(link)

    items_on_page = driver.find_element_by_class_name('b-product-gallery').find_elements_by_tag_name('li')

    data = []
    for item in items_on_page:
        link = item.find_element_by_class_name('b-product-gallery__image-link').get_attribute('href')
        data.append(get_item_data(driver, link))
        break ### Тестовое ограничение на 1 элемент [!!!]

    return data

def main():
    print('Connecting to website...')
    driver = connect()
    
    links = get_all_node_links(driver) 

    for link in links:
        print(load_all_items(driver, link))
        break ### Тестовое ограничение на 1 элемент [!!!]


if __name__ == '__main__':
    main()