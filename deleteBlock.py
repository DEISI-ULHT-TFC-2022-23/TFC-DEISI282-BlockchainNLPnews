from pymongo import MongoClient
import time

def deleteBlock(index):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    blockchain = db["chain"]

    

    if index!=0:
        result = blockchain.delete_one({"index": index})
        if result.deleted_count == 1:
            print("Block deleted successfully.")
            time.sleep(2)
        else:
            print("Block not found.")
            time.sleep(2)

    return

