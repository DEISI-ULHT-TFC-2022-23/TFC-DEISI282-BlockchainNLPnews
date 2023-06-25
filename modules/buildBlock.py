import os
import pprint
import time
from modules.blockchain import Blockchain
from .normalizeString import normalizeString

def buildBlock(blockchainInfo):

    time.sleep(1.7)

    # new instance of the blockchain
    bc = Blockchain() 
    numArticlesProcess = 100  
    
    while blockchainInfo:

        inProcess = blockchainInfo[:numArticlesProcess]
        blockchainInfo = blockchainInfo[numArticlesProcess:] 

        # process each item in the batch, taking 5 items at a time
        for i in range(0, len(inProcess), 5):
            articleTitle = inProcess[i]  
            articleDate = inProcess[i+1]  
            articleAuthor = inProcess[i+2]  
            articleLink = inProcess[i+3] 
            articleBody = inProcess[i+4]  

            # normalize the article body text
            normalized_body = normalizeString(articleBody)

            # pass the normalized body text to the blockchain for mining a new block
            bc.mine_block(articleTitle, articleDate, articleAuthor, articleLink, articleBody, normalized_body)