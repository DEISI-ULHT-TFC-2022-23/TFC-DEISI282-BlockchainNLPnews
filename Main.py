from webScrapingAllArticles import *
from articlesToBlock import *
from deleteBlock import *
from exportBlockchainJSON import *
from datetime import datetime
from deleteDbChain import *
import os
import requests


from pymongo import MongoClient
def main():
    # Main Looping
    while True:
        os.system('cls')

        print("0.To exit the software")
        print("1. Webscrap all articles from website")
        print("2. delete block from the blockchain")
        print("4. export blockchain to JSON File")
        print("5. delete entire blockchain DB (if exists)\n")
        choice = input("Please select an option (0-5): ")
        if choice == '1':
            
           #function pipping, the output for the innermost function is passed the function before it, needs python >=3.8
           ## webscraping takes 2 args, max_sub_sitemaps says how many subsitemaps are extracted, and max_links how many total urls are extracted
           ## if one or both =0 they will extract all urls
            articlesToBlock(webScrapingAllArticles(1,10))

        elif choice == '2':
            choice = input("Please insert a block index ")
            deleteBlock(int(choice))
        
        elif choice == '4':
            exportBlockchainJSON()
        
        elif choice == '5':
            deleteDbChain()

        elif choice == '0':
            print("You have chosen to exit the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
