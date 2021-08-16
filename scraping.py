# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import re
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    print('Begin Scraping')
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemi_images": image_dicts(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    print('Finished Scraping')    
    return data


def mars_news(browser):
    print('Begin Scraping: Mars News')
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
    print('Finished Scraping: Mars News')
    return news_title, news_p


def featured_image(browser):
    print('Begin Scraping: Featured Mars Image')
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    print('Finished Scraping: Featured Mars Image')
    return img_url

def mars_facts():
    print('Begin Retrieving: Mars Facts Table')
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    print('Finished Retrieving: Mars Facts Table')
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


def image_dicts(browser):

    print('Begin Scraping: Mars Hemispheres')
    # Visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    # select everything in the items list: contains all needed page links and titles
    extract = []
    extract = hemi_soup.find_all('div', class_='item')

    # titles are found under div class desription as <h3 />
    title_list = sorted(re.findall(r'(?<=<h3>)(.*)(?=<\/h3)',str(extract)))

    # extract the name of image in <div item />
    image_list_page = sorted(list(set(re.findall(r'(?<=href=\")(.*)(?=\.html\")',str(extract)))))
    image_list_page = [url + x + '.html' for x in image_list_page]

    # navigate to hemi pages to collect full size image .jpg address
    image_list = []
    for page in image_list_page:
        browser.visit(page)
        browser.links.find_by_text('Sample').click()
        pic_soup = soup(browser.html, 'html.parser')
        pic_ext = pic_soup.find_all('div', class_='wide-image-wrapper')
        pic_ext = re.findall(r'(href=\")(.*)(\.jpg)',str(pic_ext))
        pic_ext = url + (pic_ext[0][1])+(pic_ext[0][2])
        image_list.append(pic_ext)

    # Build the list that holds the dictionary of each image url and title.
    counter = 0
    for x in image_list:
        temp_dict = {}
        temp_dict.update({'img_url':image_list[counter],'title':title_list[counter]})
        hemisphere_image_urls.append(temp_dict)
        counter +=1

    print('Finished Scraping: Mars Hemispheres')
    # Quit the browser
    browser.quit()

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())