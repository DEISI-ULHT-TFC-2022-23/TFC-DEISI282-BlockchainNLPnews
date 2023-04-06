from pymongo import MongoClient
import time
import hashlib
from deleteDbChain import deleteDbChain


def hashDb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    collection = db["chain"]
    if db.command("ping")["ok"] == 1 and db.name == "blockchain_db" and collection.name == "chain":
        print("connection established with the BD, hashing now")
        time.sleep(2.7)
        with open('hashes.txt', 'w') as f:
            # Iterate over all documents in the collection
            for document in collection.find():
                # Compute a hash of the document data
                document_data = str(document).encode('utf-8')
                document_hash = hashlib.sha256(document_data).hexdigest()
                # Write the hash to the file
                f.write(f"{document_hash}\n")
        
        print("File with hashes saved to project folder")
        time.sleep(2.7)
        return True

    elif db.command("ping")["ok"] == 0:
        print("Couldn't save BD hashes to file, couldn't establish a connection with the MongoDB")
        time.sleep(2.7)
        return False
        
    else:
        print("Couldn't save BD hashes to file, can't establish a connection with the blockchain DB or collection does not exist")
        time.sleep(2.7)
        return False
    

def compareHash():
    client = MongoClient("mongodb://localhost:27017/")
    db_name = "blockchain_db"
    db = client["blockchain_db"]
    collection_name = "chain"
    if db_name in client.list_database_names() and collection_name in client[db_name].list_collection_names():
        print("Connection established with the MongoDB, comparing current DB hash with file...")
        time.sleep(2.7)

        # get the collection object
        collection = client[db_name][collection_name]

        # Compute the hash of the database
        db_hash = ""
        for document in collection.find():
            document_data = str(document).encode('utf-8')
            document_hash = hashlib.sha256(document_data).hexdigest()
            db_hash += document_hash
        
        db_hash = hashlib.sha256(db_hash.encode('utf-8')).hexdigest()

        # Read the hashes from the text file and concatenate them
        try:
            with open('hashes.txt', 'r') as f:
                file_hashes = f.read().splitlines()
                file_hash = "".join(file_hashes)
                file_hash = hashlib.sha256(file_hash.encode('utf-8')).hexdigest()
            print(f"Hash of database: {db_hash}")
            print(f"Hash of text file: {file_hash}")
            time.sleep(10)

            if db_hash == file_hash:
                print("Hashes match, program can advance")
                time.sleep(2.7)
                return 0
            else:
                print("Hashes do not match, DB will be dropped to force a new download and hashing")
                deleteDbChain(False)
                time.sleep(2.7)
                return 1

        except FileNotFoundError:
            print("Text file with hash does not exist, DB will be dropped to force a new download and hashing")
            deleteDbChain()
            time.sleep(2.7)
            return 2

    elif db.command("ping")["ok"] == 0:
        print("Couldn't establish a connection with the MongoDB")
        time.sleep(2.7)
        return 3
        
    else:
        print("Can't establish a connection with the BD, blockchain DB or collection does not exist, program will continue")
        time.sleep(2.7)
        return 3
