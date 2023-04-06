from collections import OrderedDict
import os
from pymongo import MongoClient
import time


from pymongo import MongoClient
from collections import OrderedDict
import os
import time

def garbageTitles(blockTitle):
    garbage = {'AP Top News'}

    for substring in garbage:
        if substring in blockTitle:
            return True
    
    return False


def garbageLinks(unique_list):
    os.system('cls')

    print(len(unique_list))
    print("tamanho da lista de links com lixo")
    time.sleep(0.7)

    garbage = {'https://apnews.com/hub/'}

    cleanedList = list(filter(lambda url: not any(ignore in url for ignore in garbage), unique_list))

    # Remove duplicated links by passing them through a dict. Dicts in Python <3.7 preserve order.
    unique_dict = OrderedDict.fromkeys(cleanedList)

    unique_list = list(unique_dict.keys())

    # Connect to the MongoDB database and retrieve all the URLs from the blockchain collection.
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    collection = db["chain"]

    if db.command("ping")["ok"] == 1 and db.name == "blockchain_db" and collection.name == "chain":
        print("ok")
        article_links = set()

        # Get the index of the last block
        last_block = collection.find_one(sort=[("index", -1)])
        if last_block is not None:
            last_index = last_block["index"]
        else:
            last_index = 0

        # Retrieve the article links from all the blocks
        article_links = set()
        for i in range(1, last_index+1):
            block = collection.find_one({"index": i})
            if block is not None and "article_link" in block:
                article_links.add(block["article_link"])

        # Remove any matching URLs from the unique list.
        for url in unique_list:
            if url in article_links:
                print(f"Excluding the following url because it exists in the BD URL: {url}")
            time.sleep(0.1)
                

        unique_list = list(filter(lambda url: url not in article_links, unique_list))
        time.sleep(0.7)

        print(len(unique_list))
        print("tamanho da lista de links sem lixo e ja removidos os links ja existentes na blockchain")
        ##print(unique_list)
        time.sleep(7)

        if len(unique_list) != 0:
            return unique_list
        else:
            print("No new items to add to the blockchain, returning to main")
            time.sleep(2.7)
            return unique_list.clear()

    elif db.command("ping")["ok"] == 0:
        print("Print couldnt not establish a connection with the mongoDB")
        time.sleep(2.7)
        return unique_list
    else:
        print("Could not establish a connection with the blockchain DB or collection does not exist")
        print("Passing all processed links and continuing code")
        time.sleep(2.7)
        return unique_list


    
     
        
