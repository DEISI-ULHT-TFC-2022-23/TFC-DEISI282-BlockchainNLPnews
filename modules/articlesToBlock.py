import os
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import concurrent.futures
from .buildBlock import *
import unicodedata
from unidecode import unidecode
from langdetect import detect
from langdetect import detect_langs, LangDetectException
from .garbageLinks import garbageTitles
from modules.DbOps import hashDb
from modules.DbOps import deleteDbChain


def process_url(url):
    try:
        html_content = requests.get(url).text

        soup = BeautifulSoup(html_content, "html.parser")

        # Find the title tag.
        h1Tag = soup.find('h1', class_=lambda x: x and 'component-heading' in x.lower())
        h2Tag = soup.find('h2', class_=lambda x: x and 'component-heading' in x.lower())

        if h1Tag:
            title = h1Tag.text
        elif h2Tag:
            title = h2Tag.text
        else:
            title = "Title not found"
        
        normalizedTitle = unidecode(title)
        cleanedTitle = re.sub(r"[^a-zA-Z0-9,.?!;:()\'\"/\\\-_ \n\t]", "", normalizedTitle)
        cleanedTitle = re.sub(r"\n{2,}", " ", cleanedTitle)

        # Find the publication date.
        publishDate = soup.select('span[class*="Timestamp Component"]')
        date = str(publishDate[0])
        parts = date.split(">", 1)
        remainingText = parts[1]
        remainingText_parts = remainingText.split("</span", 1)
        publicationDate = remainingText_parts[0]

        # Find the author.
        bylines = soup.find_all('span', {'class': lambda c: c and 'Component-bylines' in c})
        if bylines:
            author = re.search(r'>([^<]+)<', str(bylines))
            authorName = author.group(1)
        else:
            authorName = "no author"

        # Find the article text.
        finalArticle = "No article text found"
        paragraphs = soup.find_all('p')
        if paragraphs:
            finalArticle = ""
            for article in soup.find_all('p'):
                for hyperlinks in article.find_all('a'):
                    hyperlinks.replace_with(hyperlinks.get_text())
                finalArticle += article.text
            normalizedText = unidecode(finalArticle)
            cleanedText = re.sub(r"[^a-zA-Z0-9,.?!;:()\'\"/\\\-_ \n\t]", "", normalizedText)
            cleanedText = re.sub(r"\n{2,}", " ", cleanedText)
        
        else:
            cleanedText="No article text found"

     
        # Add the extracted information to the blockchainInfo list.
        return [cleanedTitle, publicationDate, authorName, url, cleanedText]

    except requests.exceptions.RequestException:
        # Handle the loss of internet connection or any requests-related exception
        print("Error: Failed to make the request or loss of internet connection.")
        print("DB will be dropped to insure there is no data inconsistency, this will force a complete redownload next time links are extracted")
        deleteDbChain()
        return

    except Exception as e:
        # Handle any other exception that may occur during the processing
        print(f"Error: {e}")


def articlesToBlock(urls):

    
    # Rest of your code goes here

    
    os.system('cls')

    if not urls:
        return

    blockchainInfo = []
    numUrls = len(urls)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futureUrl = {}
        for i, url in enumerate(urls):
            future = executor.submit(process_url, url)
            futureUrl[future] = url

        for i, future in enumerate(concurrent.futures.as_completed(futureUrl)):
            url = futureUrl[future]
            try:
                result = future.result()
                if result is not None:
                    for item in result:
                        blockchainInfo.append(item)

            except Exception as e:
                print(f"Error while processing {url}: {e}")
                time.sleep(1.7)

            remaining_urls = numUrls - i - 1
            
            print("\n")
            print(f"Processing link {i+1}/{numUrls}: {url}")
            

            if len(blockchainInfo) == 0:
                print("Block skipped due to empty blockchainInfo")
                continue

            if garbageTitles(str(blockchainInfo[0])):
                print("Block skipped because of trash title with repetitive content in article body")
                blockchainInfo.clear()
                continue

            try:
                if (
                    str(blockchainInfo[-1]) != "No article text found"
                    and len(str(blockchainInfo[-1])) > 0
                    and not str(blockchainInfo[-1]).isspace()
                ):
                    language = detect(blockchainInfo[-1])

                    if language == "en" and not garbageTitles(str(blockchainInfo[0])):
                        buildBlock(blockchainInfo)
                        print("Block added to the chain")
                        blockchainInfo.clear()
                    elif language != "en":
                        print("Block not added because it's not in English")
                        blockchainInfo.clear()
                else:
                    print("Block not added because the article text is empty")
                    blockchainInfo.clear()

            except LangDetectException as e:
                print("Block not added because the text article has no features")
                blockchainInfo.clear()

    # Call hashing DB function and drop the DB in case a hash cannot be generated
    if not hashDb():
        print("DB could not be hashed, so its integrity cannot be guaranteed")
        print("DB will be dropped to force a redownload next time links are extracted")
        deleteDbChain()
        time.sleep(3.7)