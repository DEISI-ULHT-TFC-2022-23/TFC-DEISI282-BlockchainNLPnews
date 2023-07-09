import os
from modules.articlesToBlock import articlesToBlock
from modules.webScrapingAllArticles import *
from modules.DbOps import deleteBlock,exportBlockchainJSON,exportClassifiersJSON,deleteDbChain,deleteDbCategories,compareHash
from modules.userArticleManually import userArticleManually
from modules.sBERT import sBERT
from modules.DbOps import *
from modules.OneThousandPlots import aThousandPlots
import time

def main():
    # Main Looping
    while True:
        os.system('cls')
        
        print ("--- Scrapping Website ---")
        print("1.  Scrap ApNews to add articles to the Blockchain DB \n")
        print("--- Comparing & Plotting Operations ---")
        print("2.  Ask user to insert the body of an article and compare it with all the stored articles")
        print("3.  Divides the articles into 2 sets, 30% is testing articles, 70% is training articles sets and calculates new categories for 30% of the articles and plots them")
        print("4.  Test the program with an already classified DB with 1337 articles \n")
        print("--- DB Operations --- ")
        print("5.  Delete entire blockchain DB and stored articles (if it exists)")
        print("6.  Delete the entire DB that has the articles categories (if it exists)")
        print("7.  Delete a block from the blockchain (testing purposes)")
        print("8.  Print the number of articles stored on each BD ")
        print("9.  Export blockchain to JSON File (if it exists, only for viewing purposes)")
        print("10. Export classifiers DB to JSON (if it exists, only for viewing purposes)\n")
        print("--- Backup & Restore DB's ---")
        print("11. Backup Blockchain DB and classifiers BD to project folder")
        print("12. Restores saved Blockchain DB and classifiers BD to this system\n")
        print("0.  To exit the software \n")
    

        userChoice = input("Please select an option (0-12): ")
        print("\n")

        if userChoice == '1':
            # Needs to check if the hash of the articles BD is valid or, if it doesn't exist it will just skip and continue
            compareHash()
            os.system('cls')
            # function pipping, the output for the innermost function is passed the function before it, needs python >=3.8
            # webscraping takes 2 args, 1st is the number of xml extracted, 2nd is the number of URL's extracted from each XML
            # example (2,5) ->2*15=30 URL's extracted
            # if any or both of the args = 0 it will extract all XML's or all URL's depending on the arg
            articlesToBlock(webScrapingAllArticles())
        
        elif userChoice == '2':
            os.system('cls')
            userArticleManually()
        
        elif userChoice == '3':
            os.system('cls')
            sBERT()
        
        elif userChoice == '4':
            os.system('cls')
            aThousandPlots()
        
        elif userChoice == '5':
            os.system('cls')
            deleteDbChain()
        
        elif userChoice == '6':
            os.system('cls')
            deleteDbCategories()

        elif userChoice == '7':
            os.system('cls')
            deleteBlock()

        elif userChoice == '8':
            os.system('cls')
            countBdElements()

        elif userChoice == '9':
            os.system('cls')
            exportBlockchainJSON()    
        
        elif userChoice == '10':
            os.system('cls')
            exportClassifiersJSON()

        elif userChoice == '11':
            os.system('cls')
            backup_blockchain_db()
            backup_classifiers_db()

        elif userChoice == '12':
            os.system('cls')
            restore_blockchain_db()
            restore_classifiers_db()     
        
        elif userChoice == '0':
            print("You have chosen to exit the program.")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)


if __name__ == "__main__":
     
        main()