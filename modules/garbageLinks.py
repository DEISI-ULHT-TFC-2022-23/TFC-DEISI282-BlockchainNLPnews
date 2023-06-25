from pymongo import MongoClient
from collections import OrderedDict
import os
import time

def garbageTitles(UrlList,):
    garbage = {'AP Top News'}

    for substring in garbage:
        if substring in UrlList:
            return True
    
    return False


def garbageLinks(uniqueList,maxLinks=0):
    os.system('cls')

    finalList=[]

    # Define the substrings or patterns that should be excluded
    garbage = {'https://apnews.com/hub/', 'https://apnews.com/video'}

    # Filter out URLs that contain any of the garbage substrings
    cleanedList = [url for url in uniqueList if not any(ignore in url for ignore in garbage)]

    # Remove duplicated links by passing them through a dict. Dicts in Python <3.7 preserve order.
    unique_Dict = OrderedDict.fromkeys(cleanedList)
    uniqueList = list(unique_Dict.keys())

    print("number of urls to be processed after initial clean-up is ", len(uniqueList))
    time.sleep(3)

    # Connect to the MongoDB database and retrieve all the URLs from the blockchain collection.
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    collection = db["chain"]
    db_name = "blockchain_db"
    collection_name = "chain"


    if db.command("ping")["ok"] == 1 and db.name == "blockchain_db" and collection.name == collection_name and db_name in client.list_database_names() and collection_name in client[db_name].list_collection_names():
        print("Connection with MongoDB established. Now excluding already existing links from the database.")
        articleLinks = set()

        # Get the index of the last block
        lastBlock = collection.find_one(sort=[("index", -1)])
        if lastBlock is not None:
            last_index = lastBlock["index"]
        else:
            last_index = 0

        # Retrieve the article links from all the blocks
        articleLinks = set()
        for i in range(1, last_index+1):
            block = collection.find_one({"index": i})
            if block is not None and "article_link" in block:
                articleLinks.add(block["article_link"])

        # Remove any matching URLs from the unique list.
        for url in uniqueList:
            if url in articleLinks:
                print(f"Excluding the following URL because it exists in the database: {url}")
            time.sleep(0.01)

        uniqueList = list(filter(lambda url: url not in articleLinks, uniqueList))
        time.sleep(0.7)

        
        print("number of URLs available to be processed after removing garbage and duplicates is ",len(uniqueList), "but only ",maxLinks," will be processed")
        time.sleep(7)

        if len(uniqueList) != 0:
            if maxLinks>0:
                return uniqueList[:maxLinks]
            else:
                return uniqueList
            
        else:
            print("No new items to add to the blockchain, returning to the main program.")
            time.sleep(2.7)
            return []

    elif db.command("ping")["ok"] == 0:
        print("Couldn't establish a connection with MongoDB.")
        time.sleep(2.7)
        if maxLinks>0:
            return uniqueList[:maxLinks]
        else:
            return uniqueList
    else:
        print("Could not establish a connection with the blockchain DB or collection does not exist.")
        print("Passing all processed links and continuing with the code.")
        time.sleep(2.7)
        if maxLinks>0:
            return uniqueList[:maxLinks]
        else:
            return uniqueList