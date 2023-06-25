import requests
from bs4 import BeautifulSoup
import time
from .garbageLinks import *
import os

mainSitemapUrl = "https://apnews.com/sitemap/sitemap_index.xml"

def webScrapingAllArticles():

    os.system('cls')

    print("This program extracts and processes articles from the appnews website, the articles on the website are stored in multiple XML's files and each file contains a few hundred articles")
    print("You will be asked to specify the number of XML's to extract and the number of URLS to extract, for example:")
    print("If you ask for 2 XML's and 100 articles, the program will proccess 2*100 URL's, some articles maybe be excluded from the final results for multiple reasons")
    print("For example for not being in English or for already existing in the BD \n")

    while True:
        try:
            numXmls = int(input("How many XMLS do you want to extract: "))
            if numXmls > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    while True:
        try:
            maLinks = int(input("How many URLS do you want to extract: "))
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
        response = requests.get(sub_sitemap_url)
        subSoup = BeautifulSoup(response.content, "xml")

        urlTags = subSoup.find_all("url")
        urls = [url.find("loc").text for url in urlTags]
        numUrls += len(urls)  # Increments the counter
        time.sleep(1)

        allUrls.extend(urls)  # Adds the URLs to the list

        if maLinks > 0 and len(allUrls) >= maLinks:
            break
    
    os.system('cls')
    # Processes the extracted URLs
    print("The total number of URLs available to be extracted in this ",numXmls,"sitemap/s is: ", len(allUrls)," but only ",numXmls*maLinks, "will be processed")
    time.sleep(5)

    if maLinks > 0:
        cleanedArticleUrls = garbageLinks(allUrls,maLinks*numXmls)
    else:
        cleanedArticleUrls = garbageLinks(allUrls)

    return cleanedArticleUrls