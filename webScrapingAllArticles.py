import requests
from bs4 import BeautifulSoup
import time
from garbageLinks import *

sitemap_urls = [
    "https://apnews.com/sitemap/google-news-sitemap/google_news_sitemap_1.xml",
    "https://apnews.com/sitemap/sitemap_index.xml"
]

def process_sub_sitemap(sub_sitemap_url):
    response = requests.get(sub_sitemap_url)
    soup = BeautifulSoup(response.content, "xml")

    urls = []
    if soup.find("urlset") is not None:
        loc_tags = soup.find_all("loc")
        urls = [loc.get_text() for loc in loc_tags]

    return urls


def webScrapingAllArticles(max_sub_sitemaps=0, max_links=0):
    all_urls = []
    sub_sitemap_count = 0
    max_links_reached = False

    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, "xml")

        if soup.find("urlset") is not None or soup.find("sitemapindex") is not None:
            loc_tags = soup.find_all("loc")
            urls = [loc.get_text() for loc in loc_tags]
            print(f"{len(urls)} URLs found in sitemap")
            time.sleep(1)

            for j, url in enumerate(urls):
                ##print(f"  Processing URL {j+1}/{len(urls)}: {url}")
                time.sleep(0.1)

                if url.endswith(".xml"):
                    if max_sub_sitemaps == 0 or sub_sitemap_count < max_sub_sitemaps:
                        sub_sitemap_count += 1
                        sub_sitemap_urls = process_sub_sitemap(url)

                        if max_links > 0 and len(all_urls) + len(sub_sitemap_urls) > max_links:
                            sub_sitemap_urls = sub_sitemap_urls[:max_links - len(all_urls)]

                        all_urls.extend(sub_sitemap_urls)

                        if sub_sitemap_count == max_sub_sitemaps:
                            break

                    else:
                        print(f"  Maximum number of sub sitemaps reached ({max_sub_sitemaps}), skipping {url}")
                        time.sleep(1)
                else:
                    all_urls.append(url)

                if max_links > 0 and len(all_urls) >= max_links:
                    max_links_reached = True
                    break

            if max_links_reached or (max_sub_sitemaps > 0 and sub_sitemap_count >= max_sub_sitemaps):
                article_urls = []
                for url in all_urls:
                    if not url.endswith(".xml"):
                        article_urls.append(url)


                for element in article_urls:
                    print("processed URL ",element)
                    time.sleep(0.3)

                cleaned_article_urls = garbageLinks(article_urls)
                if cleaned_article_urls:
                    return cleaned_article_urls

        print(f"\n{len(all_urls)} URLs extracted.")
        time.sleep(1)
