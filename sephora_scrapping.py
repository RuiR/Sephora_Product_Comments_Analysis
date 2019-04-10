import sys
from urllib.request import urlopen
from urllib.request import FancyURLopener
import pandas as pd
import numpy as np
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

browser = webdriver.Chrome('/Users/ruizhang/Desktop/chromedriver')

def get_page_count(base_url):
    browser = webdriver.Chrome('/Users/ruizhang/Desktop/chromedriver')
    browser.get(base_url)
    time.sleep(1)
    page_count = 1
    pages = browser.find_elements_by_class_name("css-x544ax")
    if pages:
        following_pages = browser.find_elements_by_class_name("css-1f9ivf5")
        for page in following_pages:
            count = int(page.text)
            page_count = count
    return page_count


def get_product_list(product_type, base_url):
    browser = webdriver.Chrome('/Users/ruizhang/Desktop/chromedriver')
    products_page_count = get_page_count(base_url)
    product_list = []
    for i in range(1, products_page_count + 1):
        page_url = base_url + "?currentPage=" + str(i)
        browser.get(page_url)
        time.sleep(1)
        elem = browser.find_element_by_tag_name("body")

        no_of_pagedowns = 20

        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
            no_of_pagedowns -= 1

        post_elems = browser.find_elements_by_class_name("css-ix8km1")

        for post in post_elems:
            product_name = post.get_attribute('aria-label')
            product_link = post.get_attribute('href')
            product_list.append([product_name, product_link])
    df = pd.DataFrame(product_list, columns=['product_name', 'product_link'])
    df.to_csv('tmp/'+product_type+'_product_list.csv', index=True)


def get_product_info_and_review_info(product_type, product_index, url):
    browser.get(url)
    # close pop-up login window
    try:
        login_window = browser.find_element_by_class_name('css-fslzaf')
        login_window.click()
    except (NoSuchElementException, ElementNotVisibleException) as exceptions:
        pass

    elem = browser.find_element_by_tag_name("body")
    no_of_pagedowns = 20
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        no_of_pagedowns -= 1

    # get product details (string)
    product_details_panel = browser.find_element_by_id('tabpanel0')
    product_details = product_details_panel.find_element_by_class_name('css-pz80c5').text

    try:
        total_reviews_text = browser.find_element_by_class_name('css-j9s1kd').text
        total_reviews_count = total_reviews_text.split(' ')[0]
        if total_reviews_count == '0':
            product_info = [product_index, product_details, 0, 0, 0, 0, 0, 0, 0]
            print(product_info)
            return product_info
    except NoSuchElementException:
        pass

    total_reviews_text = browser.find_element_by_class_name('css-mzsag6').text
    total_reviews_count = total_reviews_text.split(' ')[0]
    # get reviews count of different rates
    table_id = browser.find_element_by_class_name('css-960eb6')
    rows = table_id.find_elements_by_tag_name('tr')
    rates = []
    for row in rows:
        # Get the columns (all the column 2)
        cols = row.find_elements_by_tag_name('td') #note: index start from 0, 1 is col 2
        rates.append(int(cols[2].text))

    # get overall review rate
    overall_review_text = browser.find_element_by_class_name('css-1eqf5yr').text
    overall_review = float(overall_review_text.split(' ')[0])

    product_info = [product_index, product_details, total_reviews_count, rates[0],rates[1],rates[2],rates[3],rates[4], overall_review]
    print(product_info)
    return product_info


def get_product_reviews(product_type, product_index, url):
    browser.get(url)
    # close pop-up login window
    try:
        login_window = browser.find_element_by_class_name('css-fslzaf')
        login_window.click()
    except (NoSuchElementException, ElementNotVisibleException) as exceptions:
        pass
    # t = browser.find_element_by_class_name('css-fslzaf')
    # if t:
    #     t.click()

    elem = browser.find_element_by_tag_name("body")
    no_of_pagedowns = 20
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        no_of_pagedowns -= 1
    # get total reviews count (int)
    # total_reviews_text = browser.find_element_by_class_name('css-2rg6q7').text
    # total_reviews_count = total_reviews_text.split(' ')[0]
    try:
        total_reviews_text = browser.find_element_by_class_name('css-j9s1kd').text
        total_reviews_count = total_reviews_text.split(' ')[0]
        if total_reviews_count == '0':
            return
    except NoSuchElementException:
        pass

    total_reviews_elem = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,"css-mzsag6")))
    total_reviews_text = total_reviews_elem.text
    total_reviews_count = total_reviews_text.split(' ')[0]
    try:
        next_comments = browser.find_element_by_class_name('css-1phfyoj')
        max_load_count = 84
        # load all reviews
        while next_comments and max_load_count:
            next_comments.click()
            next_comments = browser.find_element_by_class_name('css-1phfyoj')
            next_comments = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,"css-1phfyoj")))
            max_load_count -= 1
    except NoSuchElementException as exception:
        pass

    all_reviews_elements = browser.find_elements_by_css_selector("[data-comp=Review]")

    columns = ['review_user_id', 'review_user_info', 'rate', 'review_date', 'review_content',
               'not_helpful', 'helpful']

    all_reviews = []
    for review in all_reviews_elements:
        # read info from each review
        review_user_id = ''
        try:
            review_user_id = review.find_element_by_class_name('css-y7wmlg').text
        except NoSuchElementException:
            pass
        review_user_info = ''
        try:
            all_review_user_info = review.find_elements_by_class_name('css-15415he')
            review_user_info = ''
            for r in all_review_user_info:
                review_user_info += r.text
        except NoSuchElementException:
            pass
        rate = ''
        review_date = ''
        review_content = ''
        try:
            rate = review.find_element_by_class_name('css-5quttm').get_attribute('aria-label')
        except NoSuchElementException:
            pass

        try:
            review_date = review.find_element_by_class_name('css-1mfxbmj').text
        except NoSuchElementException:
            pass

        try:
            review_content = review.find_element_by_class_name('css-1p4f59m').text
        except NoSuchElementException:
            pass

        # if_recommend_this_product = review.find_element_by_class_name('css-ue839').text
        helpful = ''
        not_helpful = ''
        try:
            if_helpful = review.find_elements_by_class_name('css-lgjx3u')
            not_helpful = if_helpful[0].text
            helpful = if_helpful[1].text
        except NoSuchElementException:
            pass
        all_reviews.append(
            [review_user_id, review_user_info, rate, review_date, review_content,
             not_helpful, helpful])

    df = pd.DataFrame(all_reviews, columns=columns)
    df.to_csv('tmp_data/' + product_type + "_" + str(product_index) + '.csv', index=False)


def get_all_products_info(product_type, all_products_list):
    product_count = len(all_products_list)
    all_products_info = []
    # start_index = 7
    # Get only the first 100 products' reviews
    for i in range(min(100, product_count)):
        print(all_products_list[i][1])
        product_url = all_products_list[i][2]
        get_product_reviews(product_type, all_products_list[i][0], product_url)
        # product_info = get_product_info_and_review_info(product_type, i+start_index, product_url)
        # all_products_info.append(product_info)
    # df = pd.DataFrame(all_products_info, columns=['product_index', 'product_details', 'total_reviews_count',
    #                                               '5_star_counts','4_star_counts','3_star_counts','2_star_counts',
    #                                               '1_star_counts', 'overall_review'])
    # df.to_csv('tmp_data/'+product_type + '_all_products_info.csv', index=False)


if __name__ == '__main__':
    eye_cream_df = pd.read_csv('tmp_data/eye_cream_product_list_part.csv')
    eye_cream_list = eye_cream_df.values.tolist()
    get_all_products_info('eye_cream',eye_cream_list)
