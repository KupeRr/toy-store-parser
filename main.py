from time import sleep
import os

from selenium.webdriver import Chrome
from selenium import webdriver

MAIN_URL = r'https://zullu.com.ua/product_list'

def connect(url = MAIN_URL):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = Chrome(options=options)
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
    driver = connect(link)
    with open(f'images/{code}/img_{num}.png', 'wb') as file:
        file.write(driver.find_element_by_tag_name('img').screenshot_as_png)
    driver.close()

def save_item_images(code, driver):
    if not os.path.isdir('images'): os.mkdir('images')
    if not os.path.isdir(f'images/{code}'): os.mkdir(f'images/{code}')

    driver.find_element_by_class_name('b-product-image__img').click()
    sleep(1)

    num = int(driver.find_element_by_class_name('b-images-view__header').text.split()[-1])
    save_image(code, 1, driver.find_element_by_class_name('b-images-view__photo').get_attribute('src'))

    while True:
        driver.find_element_by_class_name('b-images-view__button_direction_right').click()
        sleep(1)

        num = int(driver.find_element_by_class_name('b-images-view__header').text.split()[-1])

        if num == 1: break

        save_image(code, num, driver.find_element_by_class_name('b-images-view__photo').get_attribute('src'))

def get_item_data(driver, link):
    driver.get(link)

    article = driver.find_element_by_class_name('b-product-data__item_type_sku').find_element_by_tag_name('span').text

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

    item_data = {
        'name'          : driver.find_element_by_class_name('b-title_type_product').find_element_by_tag_name('span').text,
        'price'         : driver.find_element_by_class_name('b-product-cost__price').find_element_by_tag_name('span').text,
        'available'     : driver.find_element_by_class_name('b-product-data__item_type_available').text,
        'article'       : article,
        'path'          : path,
        'description'   : description,
        'attribute'     : attribute,
        'link'          : link,
    }

    save_item_images(article, driver)

    return item_data

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