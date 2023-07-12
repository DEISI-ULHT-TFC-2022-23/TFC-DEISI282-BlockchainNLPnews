import os
import json
import time
import hashlib
from pymongo import MongoClient
from bson import json_util

# mongoDB connection details
connectionInfo = "mongodb://localhost:27017/"

# backup blockchain_db
def backup_blockchain_db():
    # create backup directory if it doesn't exist
    backupDirectory = os.path.join(os.path.dirname(__file__), "..", "backup")
    os.makedirs(backupDirectory, exist_ok=True)

    # connect to the MongoDB client
    client = MongoClient(connectionInfo)

    if "blockchain_db" in client.list_database_names():
        blockchainDB = client["blockchain_db"]
        blockchainCollection = blockchainDB["chain"]
        blockchainBackupPath = os.path.join(backupDirectory, "blockchain_db.bak")
        backup_documents(blockchainCollection, blockchainBackupPath)
        print("blockchain_db backup created successfully.")
    else:
        print("Warning: blockchain_db does not exist.")
        input("press ENTER to continue")

    # close the MongoDB client
    client.close()


# backup classifiers_db
def backup_classifiers_db():
    # create backup directory if it doesn't exist
    backupDirectory = os.path.join(os.path.dirname(__file__), "..", "backup")
    os.makedirs(backupDirectory, exist_ok=True)

    # connect to the MongoDB client
    client = MongoClient(connectionInfo)

    if "classifiers_db" in client.list_database_names():
        classifiersDB = client["classifiers_db"]
        classifiersCollection = classifiersDB["categories"]
        classifiersBackupPath = os.path.join(backupDirectory, "classifiers_db.bak")
        backup_documents(classifiersCollection, classifiersBackupPath)
        input("classifiers_db backup created successfully.")
    else:
        print("Warning: classifiers_db does not exist.")
        input("press ENTER to continue")

    # close the MongoDB client
    client.close()


# Backup MongoDB documents
def backup_documents(collection, backup_path):
    documents = list(collection.find())
    with open(backup_path, 'w') as backup_file:
        for document in documents:
            json.dump(document, backup_file, default=json_util.default)
            backup_file.write('\n')


# Restore blockchain_db
def restore_blockchain_db():
    # Connect to the MongoDB client
    client = MongoClient(connectionInfo)

    blockchainBackupPath = os.path.join(os.path.dirname(__file__), "..", "backup", "blockchain_db.bak")
    if os.path.isfile(blockchainBackupPath):
        blockchain_db = client["blockchain_db"]
        blockchainCollection = blockchain_db["chain"]
        existingRecords = blockchainCollection.count_documents({})
        backupRecords = getDocumentCount(blockchainBackupPath)
        print(f"Existing records in blockchain_db: {existingRecords}")
        print(f"Records in backup: {backupRecords}")

        overwrite = promptUserConfirmation("blockchain_db")
        if overwrite:
            blockchain_db.drop_collection("chain")
            restoreDocuments(blockchainCollection, blockchainBackupPath)
            hashDb()
            print("blockchain_db restored successfully.")
            input("Press ENTER to continue")
        else:
            print("blockchain_db restore canceled.")
            input("Press ENTER to continue")
    else:
        print("Error: blockchain_db backup file does not exist. \n")
        input("press ENTER to continue")

    # close the MongoDB client
    client.close()


# restore classifiers_db
def restore_classifiers_db():
    # connect to the MongoDB client
    client = MongoClient(connectionInfo)

    classifiersBackupPath = os.path.join(os.path.dirname(__file__), "..", "backup", "classifiers_db.bak")
    if os.path.isfile(classifiersBackupPath):
        classifiersDB = client["classifiers_db"]
        classifiersCollection = classifiersDB["categories"]
        existingRecords = classifiersCollection.count_documents({})
        backup_records = getDocumentCount(classifiersBackupPath)
        print(f"Existing records in classifiers_db: {existingRecords}")
        print(f"Records in backup: {backup_records}")

        forceOverwrite = promptUserConfirmation("classifiers_db")
        if forceOverwrite:
            classifiersDB.drop_collection("categories")
            restoreDocuments(classifiersCollection, classifiersBackupPath)
            print("classifiers_db restored successfully.")
            input("Press ENTER to continue")
        else:
            print("classifiers_db restore canceled.")
            input("press ENTER to continue")
    else:
        print("Error: classifiers_db backup file does not exist. \n")
        input("press ENTER to continue")

    # close the MongoDB client
    client.close()

# restore MongoDB documents
def restoreDocuments(collection, backup_path):
    with open(backup_path, 'r') as backup_file:
        first_line = backup_file.readline().strip()
        if not first_line:
            print("Warning: Backup file is empty.")
            return

        backup_file.seek(0)
        for line in backup_file:
            document = json.loads(line)

            # Exclude the '_id' field
            document.pop('_id', None)
            collection.insert_one(document)


# helper function to get the number of documents in a MongoDB backup file
def getDocumentCount(backup_path):
    with open(backup_path, 'r') as backup_file:
        return sum(1 for _ in backup_file)

# helper function to prompt user confirmation
def promptUserConfirmation(db_name):
    while True:
        user_input = input(f"Do you want to overwrite {db_name}? (y/n): ").lower()
        if user_input == "y":
            return True
        elif user_input == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


#####################################################################################################################
# the following code is exactly the same as the code above but points to the BD's with 1k articles already classified
# Restore blockchain_db

def restore1kBlockchain():
    # Connect to the MongoDB client
    client = MongoClient(connectionInfo)

    blockchainBackupPath = os.path.join(os.path.dirname(__file__), "..", "1kPlots", "blockchain_1k.bak")
    if os.path.isfile(blockchainBackupPath):
        blockchainDB = client["blockchain_1k"]
        blockchaiNCollection = blockchainDB["chain1k"]
        existingRecords = blockchaiNCollection.count_documents({})
        backupRecords = getDocumentCount(blockchainBackupPath)
       
        blockchainDB.drop_collection("chain1k")
        restoreDocuments(blockchaiNCollection, blockchainBackupPath)
        print("blockchain 1k restored successfully.")

        # close the MongoDB client
        client.close()
        return True
        
    else:
        print("Error: blockchain 1k backup file does not exist. The backup file is supposed to be inside the '1kPlots' folder")
        print("Either download that file from the git repository and move it to the folder or redownload the entire project")
        input("Press ENTER to continue")

        # close the MongoDB client
        client.close()
        return False
        
# restore classifiers_db
def restore1kClassifiers():
    # connect to the MongoDB client
    client = MongoClient(connectionInfo)

    classifiers_backup_path = os.path.join(os.path.dirname(__file__), "..", "1kPlots", "classifiers_1k.bak")
    if os.path.isfile(classifiers_backup_path):
        classifiers_db = client["classifiers_1k"]
        classifiers_collection = classifiers_db["categories1k"]
        existing_records = classifiers_collection.count_documents({})
        backup_records = getDocumentCount(classifiers_backup_path)
        

        classifiers_db.drop_collection("categories1k")
        restoreDocuments(classifiers_collection, classifiers_backup_path)
        print("classifiers 1k restored successfully.")

        # close the MongoDB client
        client.close()
        return True
    else:
        print("Error: blockchain 1k backup file does not exist. The backup file is supposed to be inside the '1kPlots' folder")
        print("Either download that file from the git repository and move it to the folder or redownload the entire project")
        input("press ENTER to continue")
        # close the MongoDB client
        client.close()
        return False


##############################################################
# other BD related operations, delete block, delete DB's, etc.
def deleteBlock():
    os.system('cls')
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    blockchain = db["chain"]

    while True:
        user_input = input("Enter the index to delete (integer): ")
        try:
            index = int(user_input)
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    if index != 0:
        result = blockchain.delete_one({"index": index})
        if result.deleted_count == 1:
            print("Block deleted successfully.")
            time.sleep(2)
        else:
            print("A block with that index does not exist, try again or export the blockchain DB to a json file to view the blockchain and choose a valid index.")
            time.sleep(2)

    return


def deleteDbCategories(warning=True):
    # Create an instance of MongoClient and pass the connection string as an argument
    client = MongoClient("mongodb://localhost:27017/")

    # Get a list of existing database names
    database_names = client.list_database_names()

    # Check if the database name exists in the list of database names
    if "classifiers_db" in database_names:
        # Check if the categories collection exists in the classifiers_db
        if "categories" in client["classifiers_db"].list_collection_names():
            # Drop the categories collection
            client["classifiers_db"].drop_collection("categories")
            print("Categories collection dropped")

        # Drop the classifiers_db database
        client.drop_database("classifiers_db")
        print("Classifiers database dropped")
        input("Press ENTER to continue")

    elif warning:
        input("Categories database does not exist. Press ENTER to continue")


def deleteDbChain(warning=True):
    # Create an instance of MongoClient and pass the connection string as an argument
    client = MongoClient("mongodb://localhost:27017/")

    # Get a list of existing database names
    database_names = client.list_database_names()

    # Check if the database name exists in the list of database names
    if "blockchain_db" in database_names:
        # Drop the database
        client.drop_database("blockchain_db")
        input("blockchain database was dropped, DB will be redownloaded, press ENTER to continue")


    elif warning==True: 
        print("blockchain database does not exist")
        input("press ENTER to continue")


def exportBlockchainJSON():
    # Create a MongoDB client and connect to the blockchain_db database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    chain = db["chain"]

    # Retrieve all documents from the chain collection
    documents = chain.find()

    # Serialize each document to a JSON string
    serializedData = ""
    for document in documents:
        # Convert the ObjectId to string
        document["_id"] = str(document["_id"])
        serializedData += json.dumps(document, indent=4) + "\n"

    # Get the current directory of your script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level
    projectFolderPath = os.path.dirname(current_dir)

    # Create the path to the "output Files" subfolder
    outputFolderPath = os.path.join(projectFolderPath, "output Files")

    # Create the "output Files" folder if it doesn't exist
    os.makedirs(outputFolderPath, exist_ok=True)

    # Create the file path by concatenating the output folder path with the filename
    outputFilepath = os.path.join(outputFolderPath, "blockchain.json")

    # Write the serialized data to a file in the output folder
    with open(outputFilepath, "w") as f:
        f.write(serializedData)

    # Print a message indicating that the file was created
    print("Blockchain data exported to:", outputFilepath)
    input("Press ENTER to continue")


def exportClassifiersJSON():
    # Create a MongoDB client and connect to the classifiers_db database
    client = MongoClient("mongodb://localhost:27017/")
    db = client["classifiers_db"]
    categories = db["categories"]

    # Retrieve all documents from the categories collection
    documents = categories.find()

    # Serialize each document to a JSON string
    serializedData = ""
    for document in documents:
        # Convert the ObjectId to string
        document["_id"] = str(document["_id"])
        serializedData += json.dumps(document, indent=4) + "\n"

    # Get the current directory of your script
    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    # Go up one level
    projectFolderPath = os.path.dirname(currentDirectory)

    # Create the path to the "output Files" subfolder
    outputFolderPath = os.path.join(projectFolderPath, "output Files")

    # Create the "output Files" folder if it doesn't exist
    os.makedirs(outputFolderPath, exist_ok=True)

    # Create the file path by concatenating the output folder path with the filename
    filepath = os.path.join(outputFolderPath, "classifiers.json")

    # Write the serialized data to a file in the output folder
    with open(filepath, "w") as f:
        f.write(serializedData)

    # Print a message indicating that the file was created
    print("Classifiers data exported to:", filepath)
    input("Press ENTER to continue")

###################################################
#hash functions
def hashDb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    collection = db["chain"]
    if db.command("ping")["ok"] == 1 and db.name == "blockchain_db" and collection.name == "chain":
        print("Connection established with the DB, hashing now")
        time.sleep(2.7)
        
        # Read the existing hashes from the file
        fileHashes = []
        try:
            with open('hashes.txt', 'r') as f:
                fileHashes = f.readlines()
        except FileNotFoundError:
            print("Text file with hash does not exist, DB will be dropped to force a new download and hashing")
            deleteDbChain()
            time.sleep(2.7)
            return 2
        
        # Compute the hash of the database
        db_Hash = hashlib.sha256()
        for document in collection.find():
            # Remove the _id field before hashing
            if "_id" in document:
                del document["_id"]
            # Compute a hash of the document data
            documentData = json.dumps(document, default=json_util.default, sort_keys=True).encode('utf-8')
            db_Hash.update(documentData)

        db_Hash = db_Hash.hexdigest()
        
        # Overwrite the first line with the new hash
        fileHashes[0] = f'{{"current DB hash": "{db_Hash}"}}\n'

        # Write the updated hashes to the file
        with open('hashes.txt', 'w') as f:
            f.writelines(fileHashes)
        
        print("File with hashes saved to project folder")
        time.sleep(2.7)
        return db_Hash

    elif db.command("ping")["ok"] == 0:
        print("Couldn't save DB hashes to file, couldn't establish a connection with MongoDB")
        time.sleep(2.7)
        return None
        
    else:
        print("Couldn't save DB hashes to file, can't establish a connection with the blockchain DB or collection does not exist")
        time.sleep(2.7)
        return None
    

def compareHash():
    client = MongoClient("mongodb://localhost:27017/")
    db_name = "blockchain_db"
    db = client["blockchain_db"]
    collectionName = "chain"
    if db_name in client.list_database_names() and collectionName in client[db_name].list_collection_names():
        print("Connection established with MongoDB, comparing current DB hash with file... \n")
        time.sleep(2.7)

        # Get the collection object
        collection = client[db_name][collectionName]

        # computes the hash of the DB
        dbHash = hashlib.sha256()
        for document in collection.find():
            # Remove the _id field before hashing
            if "_id" in document:
                del document["_id"]
            documentData = json.dumps(document, default=json_util.default, sort_keys=True).encode('utf-8')
            dbHash.update(documentData)
        
        dbHash = dbHash.hexdigest()

        # reads the hashes from the text file and compares
        try:
            with open('hashes.txt', 'r') as f:
                file_hashes = f.readlines()
                file_hash = ""
                for line in file_hashes:
                    if "current DB hash" in line:
                        file_hash = line.split(":")[1].strip().strip('",}')
                        break
                print(f"Hash of database:  {dbHash}")
                print(f"Hash of text file: {file_hash} \n")
                time.sleep(10)

                if dbHash == file_hash:
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
        print("Couldn't establish a connection with MongoDB")
        time.sleep(2.7)
        return 3
        
    else:
        print("Can't establish a connection with the DB, blockchain DB, or collection does not exist, the program will continue")
        time.sleep(2.7)
        return 3

def countBdElements():

    os.system('cls')

    # Connect to the MongoDB database and retrieve the chain collection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["blockchain_db"]
    collection = db["chain"]

    db_name = "blockchain_db"
    collection_name = "chain"

    # Check if the database and collection exist and if the connection is successful
    if db.command("ping")["ok"] == 1 and db_name in client.list_database_names() and collection_name in db.list_collection_names():
        print("Connection to the blockchain database successful")
        time.sleep(0.7)
    
    
    dbCat = client["classifiers_db"]
    collectionCat = dbCat["categories"]

    # Check if the database and collection exist and if the connection is successful
    if dbCat.command("ping")["ok"] == 1 and "categories" in dbCat.list_collection_names():
        print("Connection to the categories collection successful \n")
        time.sleep(0.7)

        
    # number of articles in the blockchain DB, -1 is because of the genesis block
    # forces the number to become=0 if it's negative
    print("The number of stored articles in the blockchain BD is ", max(collection.count_documents({}) - 1, 0))

    # count the number of records in the classifiers BD
    print("The number of already classified articles in the classifiers BD is ", max(collectionCat.count_documents({}) - 1, 0))
    input("Press ENTER to continue")

    