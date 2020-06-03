import os
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
import time


def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape_info():
    browser = init_browser()    
    
    # NASA Mars News
    
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)
    
    time.sleep(5)
    
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news_titles = soup.find_all('div', class_='content_title')
    news_list = []
    
    for news in news_titles:
        if news.a:
            news_list.append(news.a.text.strip())
    
    news_title = news_list[0]
    news_text = soup.find_all('div', class_='article_teaser_body')
    news_p = news_text[0].text.strip()
    
    # JPL Mars Space Images - Featured Image
    
    base_url = 'https://www.jpl.nasa.gov' 
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    image_link = soup.find('div', class_='carousel_items')
    image_urls = image_link.article["style"].split()[1]
    featured_image_url = image_urls.replace("url('", base_url).replace("');","")
    # response = requests.get(featured_image_url, stream=True)
    # with open('featured_img.png', 'wb') as out_file:
    #     shutil.copyfileobj(response.raw, out_file)
    
    # Mars Facts
    
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[1]
    df.set_index('Mars - Earth Comparison', inplace=True)
    html_table = df.to_html()
    df.to_html('table.html')
    
    # Mars Hemisphere
    
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.find_all('div', class_='item')

    hemisphere_url = []

    for product in products:
        link = product.a["href"]
        hemisphere_url.append('https://astrogeology.usgs.gov/'+link)
    
    hemisphere_image_urls = []
    page_titles = []
    page_links = []

    for url in hemisphere_url:
        browser.visit(url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        titles = soup.find_all('title')
        links = soup.find_all('div', class_="downloads")
    
        for title in titles:
            page_titles.append(title.text.replace("| USGS Astrogeology Science Center", ""))
        for link in links:
            page_links.append(link.ul.li.a["href"])

    hemisphere_image_urls = [{'title': x, 'img_url': y} for x, y in zip(page_titles, page_links)]
    
    browser.quit()

    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_mars_image": featured_image_url,
        "mars_table": html_table,
        "hemisphere_images" : hemisphere_image_urls
    }
    
    return mars_data