import requests
from bs4 import BeautifulSoup
import time
from .garbageLinks import *
import os

mainSitemapUrl = "https://apnews.com/sitemap.xml"

def webScrapingAllArticles():

    os.system('cls')
    skipfirst=False

    print("This program extracts and processes articles from the apnews website, the articles on the website are stored in multiple XML files and each file contains a few hundred articles")
    print("You will be asked to specify the number of XMLs to extract and the number of URLs to extract, for example:")
    print("If you ask for 2 XMLs and 100 articles, the program will process 2*100 URLs. Some articles may be excluded from the final results for various reasons.")
    print("For example, if they are not in English or if they already exist in the database. \n")

    while True:
        try:
            numXmls = int(input("How many XMLs do you want to extract: "))
            if numXmls > 0:
                if numXmls==1:
                    numXmls+=1
                    skipfirst=True
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    while True:
        try:
            maLinks = int(input("How many URLs do you want to extract: "))
            if maLinks > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    allUrls = []
    numUrls = 0  # Adds a counter for the number of URLs found

    response = requests.get(mainSitemapUrl)
    soup = BeautifulSoup(response.content, "xml")

    sitemapTags = soup.find_all("sitemap")
    subSitemapUrls = [sitemap.find("loc").text for sitemap in sitemapTags]
    subSitemapUrls = subSitemapUrls[-numXmls:] if numXmls > 0 else subSitemapUrls

    for sub_sitemap_url in subSitemapUrls:
        if sub_sitemap_url == "https://apnews.com/sitemap-latest.xml":
            continue  # Skip processing this XML if it matches the specified URL

        response = requests.get(sub_sitemap_url)
        subSoup = BeautifulSoup(response.content, "xml")

        urlTags = subSoup.find_all("url")
        urls = [url.find("loc").text for url in urlTags]
        numUrls += len(urls)  # Increments the counter
        time.sleep(1)

        allUrls.extend(urls)  # Adds the URLs to the list

        if maLinks > 0 and len(allUrls) >= maLinks:
            break

    if skipfirst:
        numXmls=1
    os.system('cls')
    # Processes the extracted URLs
    print("The total number of URLs available to be extracted in this", numXmls, "sitemap/s is:", len(allUrls), "but only", numXmls * maLinks, "will be processed")
    time.sleep(5)

    if maLinks > 0:
       
        cleanedArticleUrls = garbageLinks(allUrls, maLinks * numXmls)
    else:
        cleanedArticleUrls = garbageLinks(allUrls)

    return cleanedArticleUrls
