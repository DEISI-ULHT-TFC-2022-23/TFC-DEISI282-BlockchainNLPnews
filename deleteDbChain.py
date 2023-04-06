import os
from pymongo import MongoClient

def deleteDbChain():
    # Create an instance of MongoClient and pass the connection string as an argument
    client = MongoClient("mongodb://localhost:27017/")

    # Get a list of existing database names
    database_names = client.list_database_names()

    # Check if the database name exists in the list of database names
    if "blockchain_db" in database_names:
        # Drop the database
        client.drop_database("blockchain_db")
        input("blockchain database was dropped")

    else: 
        input("blockchain database not found")
