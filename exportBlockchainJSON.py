import os
import json
from pymongo import MongoClient

def exportBlockchainJSON():
    # Create a MongoDB client and connect to the blockchain_db database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    chain = db["chain"]

    # Retrieve all documents from the chain collection
    documents = chain.find()

    # Serialize each document to a JSON string
    serialized_data = ""
    for document in documents:
        # Convert the ObjectId to string
        document["_id"] = str(document["_id"])
        serialized_data += json.dumps(document, indent=4) + "\n"

    # Create the file path by concatenating the current working directory with the filename
    filepath = os.path.join(os.getcwd(), "blockchain.json")

    # Write the serialized data to a file in the current directory
    with open(filepath, "w") as f:
        f.write(serialized_data)

    # Print a message indicating that the file was created
    print("Blockchain data exported to:", filepath)
    input("Press ENTER to continue")
