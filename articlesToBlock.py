import os
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import concurrent.futures
from buildBlock import *
import unicodedata
from unidecode import unidecode
from langdetect import detect
from langdetect import detect_langs, LangDetectException
from garbageLinks import garbageTitles
from hashDb import hashDb
from deleteDbChain import deleteDbChain


def process_url(url):
    try:
        html_content = requests.get(url).text

        soup = BeautifulSoup(html_content, "html.parser")

        # Find the title tag.
        h1_tag = soup.find('h1', class_=lambda x: x and 'component-heading' in x.lower())
        h2_tag = soup.find('h2', class_=lambda x: x and 'component-heading' in x.lower())

        if h1_tag:
            title = h1_tag.text
        elif h2_tag:
            title = h2_tag.text
        else:
            title = "Title not found"
        
        normalized_title = unidecode(title)
        cleaned_title = re.sub(r"[^a-zA-Z0-9,.?!;:()\'\"/\\\-_ \n\t]", "", normalized_title)
        cleaned_title = re.sub(r"\n{2,}", " ", cleaned_title)

        # Find the publication date.
        time_element = soup.select('span[class*="Timestamp Component"]')
        date = str(time_element[0])
        parts = date.split(">", 1)
        remaining_text = parts[1]
        remaining_text_parts = remaining_text.split("</span", 1)
        publication_date = remaining_text_parts[0]

        # Find the author.
        bylines = soup.find_all('span', {'class': lambda c: c and 'Component-bylines' in c})
        if bylines:
            author = re.search(r'>([^<]+)<', str(bylines))
            author_name = author.group(1)
        else:
            author_name = "no author"

        # Find the article text.
        finalArticle = "No article text found"
        paragraphs = soup.find_all('p')
        if paragraphs:
            finalArticle = ""
            for article in soup.find_all('p'):
                for hyperlinks in article.find_all('a'):
                    hyperlinks.replace_with(hyperlinks.get_text())
                finalArticle += article.text
            normalized_text = unidecode(finalArticle)
            cleaned_text = re.sub(r"[^a-zA-Z0-9,.?!;:()\'\"/\\\-_ \n\t]", "", normalized_text)
            cleaned_text = re.sub(r"\n{2,}", " ", cleaned_text)
        
        else:
            cleaned_text="No article text found"

     
        # Add the extracted information to the blockchain_info list.
        return [cleaned_title, publication_date, author_name, url, cleaned_text]

    except Exception as e:
        print(f"Error while processing {url}: {e}")


def articlesToBlock(urls):

    if not urls:
        return

    blockchain_info = []
    num_urls = len(urls)

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {}
        for i, url in enumerate(urls):
            future = executor.submit(process_url, url)
            future_to_url[future] = url

        for i, future in enumerate(concurrent.futures.as_completed(future_to_url)):
            url = future_to_url[future]
            try:
                result = future.result()
                if result is not None:
                    for item in result:
                        blockchain_info.append(item)

            except Exception as e:
                print(f"Error while processing {url}: {e}")
                time.sleep(1.7)

            remaining_urls = num_urls - i - 1
            print(f"Processing link  {i+1}/{num_urls} {url}")
            time.sleep(0.3)

            ##print(blockchain_info[-1])
            ##time.sleep(3.7)

            if garbageTitles(str(blockchain_info[0]))==True:
                print("Block skipped because of trash title with repetitive content in article body")
                blockchain_info.clear()
                time.sleep(2.7)

            else:

                try:
                    if str(blockchain_info[-1])!="No article text found" or len(str(blockchain_info[-1])) == 0 or str(blockchain_info[-1]).isspace() :
                        language = detect(blockchain_info[-1])

                        if  language == 'en' and garbageTitles(str(blockchain_info[0]))==False:           
                            buildBlock(blockchain_info)
                            blockchain_info.clear()
                        
                        elif language!='en':
                            print("Block not added because its not in english")
                            blockchain_info.clear()
                            time.sleep(1.7)
                        

                except LangDetectException as e:
                    print(f"Block not added because the text article has no features")
                    blockchain_info.clear()
                    time.sleep(1.7)
    
    ##call hashing DB function and dropping the BD in case a hash cannot be generated
    if not hashDb():
        print("DB could not be hashed so its integrity cannot be guaranteed")
        print("BD will be dropped to force a redownload next time links are extracted")
        deleteDbChain()
        time.sleep(3.7)  
