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
        response = requests.get(url)
        
        # Check if the response was successful
        if response is not None and response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Find the title tag in h1 or h2.
            h1Tag = soup.find('h1', class_=lambda x: x and 'Page-headline' in x)
            h2Tag = soup.find('h2', class_=lambda x: x and 'Page-headline' in x)

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
            publishDateTag = soup.find('div', class_='Page-datePublished')
            if publishDateTag:
                timestampTag = publishDateTag.find('span', {'data-date': True})
                if timestampTag and 'data-date' in timestampTag.attrs:
                    publicationDate = timestampTag['data-date'].strip()
                else:
                    publicationDate = "Publication date not found"
            else:
                publicationDate = "Publication date not found"

            # Find the author.
            authorTag = soup.find('div', class_="Page-authors")
            authorName = authorTag.find('span', class_="Link").text if authorTag else "Author not found"

            # Find the article text.
            articleTags = soup.find_all('p')
            if articleTags:
                finalArticle = ""
                for article in articleTags:
                    for hyperlinks in article.find_all('a'):
                        hyperlinks.replace_with(hyperlinks.get_text())
                    finalArticle += article.text
                normalizedText = unidecode(finalArticle)
                cleanedText = re.sub(r"[^a-zA-Z0-9,.?!;:()\'\"/\\\-_ \n\t]", "", normalizedText)
                cleanedText = cleanedText.translate(str.maketrans("", "", "\\"))
                cleanedText = re.sub(r"\n{2,}", " ", cleanedText)
            else:
                cleanedText = "No article text found"

            # Add the extracted information to the blockchainInfo list.
            return [cleanedTitle, publicationDate, authorName, url, cleanedText]
        
        else:
            return None

    except requests.exceptions.RequestException:
        # Handle the loss of internet connection or any requests-related exception
        return None

    except AttributeError:
        # Handle the case when 'NoneType' object has no attribute 'text'
        return None

    except Exception:
        # Handle any other exception that may occur during the processing
        return None


def articlesToBlock(urls):
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

            except Exception:
                continue

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

            except LangDetectException:
                print("Block not added because the text article has no features")
                blockchainInfo.clear()

    # Call hashing DB function and drop the DB in case a hash cannot be generated
    if not hashDb():
        print("DB could not be hashed, so its integrity cannot be guaranteed")
        print("DB will be dropped to force a redownload next time links are extracted")
        deleteDbChain()
        time.sleep(3.7)
