import datetime as _dt
import hashlib as _hashlib
import json as _json
from pymongo import MongoClient
import os

class Blockchain:
    connectionActive = False
    client = None  # initializes the client variable

    def __init__(self):
        if not Blockchain.connectionActive:
            # starts a connection to mongoDB 
            Blockchain.client = MongoClient("mongodb://localhost:27017/")
            try:
                # checks if the connection is alive
                Blockchain.client.server_info()
                print("Connection with the database active")
                Blockchain.connectionActive = True
            except:
                print("Not connected to the database")
                return

        db = Blockchain.client["blockchain_db"]
        self.chain = db["chain"]

        # creates a blockchain collection if it doesn't exist
        if not db.list_collection_names():
            db.create_collection("chain")

        if self.chain.count_documents({}) == 0:
            # creates the genesis block and adds it to the chain collection
            genesisBlock = {
                "index": 1,
                "blockTimestamp": str(_dt.datetime.now()),
                "proof": 1,
                "previous_hash": "0",
                "article_title": "I'm the genesis block",
                "article_date": 0,
                "article_author": "null",
                "article_link": "null",
                "article_body": "null",
                "normalized_body": "null"  # adds the normalized body field
            }
            genesisBlock["_id"] = self._get_block_id(
                articleTitle=genesisBlock["article_title"],
                articleDate=genesisBlock["article_date"],
                articleAuthor=genesisBlock["article_author"],
                articleLink=genesisBlock["article_link"],
                articleBody=genesisBlock["article_body"],
            )
            self.chain.insert_one(genesisBlock)


    def _get_block_id(
        self,
        articleTitle: str,
        articleDate: str,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
    ) -> str:
        # concatenates all the articles parts and hashes the result to generate a unique ID
        article_string = articleTitle + str(articleDate) + articleAuthor + articleLink + articleBody
        article_hash = _hashlib.sha256(article_string.encode()).hexdigest()
        return article_hash
    

    def _create_block(
        self,
        proof: int,
        previous_hash: str,
        index: int,
        articleTitle: str,
        articleDate: int,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
        normalized_body: str,  # adds the normalized body parameter
    ) -> dict:
        # creates a new block using the article data
        block = {
            "index": index,
            "blockTimestamp": str(_dt.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "article_title": articleTitle,
            "article_date": articleDate,
            "article_author": articleAuthor,
            "article_link": articleLink,
            "article_body": articleBody,
            "normalized_body": normalized_body  # stores the normalized body in the block
        }
        return block
    

    def mine_block(
        self,
        articleTitle: str,
        articleDate: str,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
        normalizedBody: str,  # adds the normalized body parameter
    ) -> dict:
        # mines a new block and adds it to the chain
        previousBlock = self.get_previous_block()
        previousProof = previousBlock["proof"]
        index = self.chain.count_documents({}) + 1
        proof = self._proof_of_work(
            previousProof,
            index,
            articleTitle,
            articleDate,
            articleAuthor,
            articleLink,
            articleBody,
        )
        previous_hash = self._hash(block=previousBlock)
        block = self._create_block(
            proof=proof,
            previous_hash=previous_hash,
            index=index,
            articleTitle=articleTitle,
            articleDate=articleDate,
            articleAuthor=articleAuthor,
            articleLink=articleLink,
            articleBody=articleBody,
            normalized_body=normalizedBody,  # stores the normalized body in the block
        )
        block["_id"] = self._get_block_id(
            articleTitle=articleTitle,
            articleDate=articleDate,
            articleAuthor=articleAuthor,
            articleLink=articleLink,
            articleBody=articleBody,
        )
        self.chain.insert_one(block)
        return block
    

    def _hash(self, block: dict) -> str:
        # converts the ObjectId to a string
        block["_id"] = str(block["_id"])
        encodedBlock = _json.dumps(block, sort_keys=True).encode()
        return _hashlib.sha256(encodedBlock).hexdigest()

    def _to_digest(
        self,
        new_proof: int,
        previous_proof: int,
        index: str,
        articleTitle: str,
        articleDate: str,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
    ) -> bytes:
        # creates a digest that serves as a proof of work
        to_digest = (
            str(new_proof ** 2 - previous_proof ** 2 + index)
            + articleTitle
            + str(articleDate)
            + articleAuthor
            + articleLink
            + articleBody
        )
        return to_digest.encode()
    

    def _proof_of_work(
        self,
        previous_proof: int,
        index: int,
        articleTitle: str,
        articleDate: int,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
    ) -> int:
        # executes proof of work to find a valid proof
        new_proof = 1
        check_proof = False
        while not check_proof:
            to_digest = self._to_digest(
                new_proof,
                previous_proof,
                index,
                articleTitle,
                articleDate,
                articleAuthor,
                articleLink,
                articleBody,
            )
            hashValue = _hashlib.sha256(to_digest).hexdigest()
            if hashValue[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    

    def get_previous_block(self) -> dict:
        # gets the previous block in the chain
        lastIndex = self.chain.count_documents({})
        return self.chain.find_one({"index": lastIndex})
    

    def is_chain_valid(self) -> bool:
        # checks the validity of the blockchain DB
        previous_block = self.chain.find_one({"index": 1})
        blockIndex = 2
        while blockIndex <= self.chain.count_documents({}):
            block = self.chain.find_one({"index": blockIndex})
            if block["previous hash"] != self._hash(previous_block):
                return False
            current_proof = previous_block["proof"]
            (
                next_index,
                next_proof,
                next_articleTitle,
                next_articleDate,
                next_articleAuthor,
                next_articleLink,
                next_articleBody,
            ) = (
                block["index"],
                block["proof"],
                block["article title"],
                block["article date"],
                block["article author"],
                block["article link"],
                block["article body"],
            )
            hashValue = _hashlib.sha256(
                self._to_digest(
                    new_proof=next_proof,
                    previous_proof=current_proof,
                    index=next_index,
                    articleTitle=next_articleTitle,
                    articleDate=next_articleDate,
                    articleAuthor=next_articleAuthor,
                    articleLink=next_articleLink,
                    articleBody=next_articleBody,
                )
            ).hexdigest()

            if hashValue[:4] != "0000":
                return False

            previous_block = block
            blockIndex += 1
        return True

    # methods for interacting with MongoDB

    def get_block_by_index(self, index: int) -> dict:
        # fecthes a block from the chain by its index
        return self.chain.find_one({"index": index})
    

    def get_all_blocks(self) -> list:
        # fetches all blocks in the chain
        return list(self.chain.find({}))