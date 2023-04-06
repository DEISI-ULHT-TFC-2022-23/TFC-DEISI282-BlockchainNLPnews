import datetime as _dt
import hashlib as _hashlib
import json as _json
from pymongo import MongoClient
import os
import hashlib

import datetime as _dt
import hashlib as _hashlib
import json as _json
from pymongo import MongoClient


import datetime as _dt
import hashlib as _hashlib
import json as _json
from pymongo import MongoClient
import os

class Blockchain:
    
    def __init__(self) -> None:
        client = MongoClient("mongodb://localhost:27017/")
        try:
            client.server_info()
            print("Connection with the database active")
        except:
            print("Not connected to the database")
            return

        db = client["blockchain_db"]
        self.chain = db["chain"]

        # Create blockchain collection if it doesn't exist
        if not db.list_collection_names():
            db.create_collection("chain")

        if self.chain.count_documents({}) == 0:
            genesis_block = {
                "index": 1,
                "blockTimestamp": str(_dt.datetime.now()),
                "proof": 1,
                "previous_hash": "0",
                "article_title": "I'm the genesis block",
                "article_date": 0,
                "article_author": "null",
                "article_link": "null",
                "article_body": "null"
            }
            genesis_block["_id"] = self._get_block_id(
                articleTitle=genesis_block["article_title"],
                articleDate=genesis_block["article_date"],
                articleAuthor=genesis_block["article_author"],
                articleLink=genesis_block["article_link"],
                articleBody=genesis_block["article_body"],
            )
            self.chain.insert_one(genesis_block)

    def _get_block_id(
        self,
        articleTitle: str,
        articleDate: str,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
    ) -> str:
        # Concatenate article properties and hash the result to get a unique identifier
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
    ) -> dict:
        block = {
            "index": index,
            "blockTimestamp": str(_dt.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "article_title": articleTitle,
            "article_date": articleDate,
            "article_author": articleAuthor,
            "article_link": articleLink,
            "article_body": articleBody
        }
        return block



    def mine_block(
        self,
        articleTitle: str,
        articleDate: str,
        articleAuthor: str,
        articleLink: str,
        articleBody: str,
    ) -> dict:
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = self.chain.count_documents({}) + 1
        proof = self._proof_of_work(
            previous_proof,
            index,
            articleTitle,
            articleDate,
            articleAuthor,
            articleLink,
            articleBody,
        )
        previous_hash = self._hash(block=previous_block)
        block = self._create_block(
            proof=proof,
            previous_hash=previous_hash,
            index=index,
            articleTitle=articleTitle,
            articleDate=articleDate,
            articleAuthor=articleAuthor,
            articleLink=articleLink,
            articleBody=articleBody,
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
        # Convert the ObjectId to string
        block["_id"] = str(block["_id"])
        encoded_block = _json.dumps(block, sort_keys=True).encode()
        return _hashlib.sha256(encoded_block).hexdigest()

    def _to_digest(
        self, new_proof: int, previous_proof: int, index: str, articleTitle: str, articleDate: str, articleAuthor: str, articleLink: str, articleBody: str,) -> bytes:
        to_digest = (str(new_proof**2 - previous_proof**2 + index) + articleTitle  + str(articleDate) + articleAuthor + articleLink + articleBody)
        return to_digest.encode()

    def _proof_of_work(
        self, previous_proof: int, index: int, articleTitle: str, articleDate: int, articleAuthor: str, articleLink: str, articleBody: str,) -> int:
        new_proof = 1
        check_proof = False
        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, articleTitle, articleDate, articleAuthor, articleLink, articleBody,
            )
            hash_value = _hashlib.sha256(to_digest).hexdigest()
            if hash_value[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def get_previous_block(self) -> dict:
        last_index = self.chain.count_documents({})
        return self.chain.find_one({"index": last_index})

    def is_chain_valid(self) -> bool:
        previous_block = self.chain.find_one({"index": 1})
        block_index = 2
        while block_index <= self.chain.count_documents({}):
            block = self.chain.find_one({"index": block_index})
            if block["previous hash"] != self._hash(previous_block):
                return False
            current_proof = previous_block["proof"]
            (
                next_index, next_proof, next_articleTitle, next_articleDate, next_articleAuthor, next_articleLink, next_articleBody,) = (
                block["index"], block["proof"], block["article title"], block["article date"], block["article author"], block["article link"], block["article body"],)
            hash_value = _hashlib.sha256(
                self._to_digest(
                    new_proof=next_proof, previous_proof=current_proof, index=next_index, articleTitle=next_articleTitle,  articleDate=next_articleDate, articleAuthor=next_articleAuthor, articleLink=next_articleLink,
                    articleBody=next_articleBody,
                )
            ).hexdigest()

            if hash_value[:4] != "0000":
                return False

            previous_block = block
            block_index += 1
        return True

    # New methods for interacting with MongoDB

    def get_block_by_index(self, index: int) -> dict:
        return self.chain.find_one({"index": index})

    def get_all_blocks(self) -> list:
        return list(self.chain.find({}))