import os
import pprint
import blockchain
import time

def buildBlock(blockchainInfo):
    time.sleep(10.7)   
    bc = blockchain.Blockchain()
    batch_size = 100
    ##os.system('cls')

    while blockchainInfo:
        batch = blockchainInfo[:batch_size]
        blockchainInfo = blockchainInfo[batch_size:]
        for i in range(0, len(batch), 5):
            articleTitle = batch[i]
            articleDate = batch[i+1]
            articleAuthor = batch[i+2]
            articleLink = batch[i+3]
            articleBody = batch[i+4]
            # print("-----------")
            # print("!!!!!!!!!!!!1")
            # print(articleTitle , end='\n')
            # print(articleDate , end='\n')
            # print(articleAuthor , end='\n')
            # print(articleLink , end='\n')
            # print(articleBody , end='\n')
            bc.mine_block(articleTitle, articleDate, articleAuthor, articleLink, articleBody)
              
    ##input("Final blockchain")


