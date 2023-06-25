import os
import json

def sortJSONsDescWeights():
    # Gets the current script directory
    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    # Gets the parent directory (one level above)
    parentDirectory = os.path.abspath(os.path.join(currentDirectory, os.pardir))

    # Specifies the directory name
    outputDirectory = os.path.join(parentDirectory, "output Files")

    # Checks if the directory exists
    if not os.path.exists(outputDirectory):
        print(f"Error: Directory 'output Files' not found in {parentDirectory}")
        return

    # Specifies the list of filenames to process
    filenames = [
        "30clash70_angular.json",
        "30clash70_cosine.json",
        "30clash70_euclidean.json",
        "30clash70_minkowski.json"
    ]

    # Checks if all required files exist
    missingFiles = []
    for filename in filenames:
        filepath = os.path.join(outputDirectory, filename)
        if not os.path.exists(filepath):
            missingFiles.append(filename)

    if missingFiles:
        print(f"Error: The following files are missing in the 'output Files' directory:")
        for filename in missingFiles:
            print(filename)
        return

    # Processes the existing files
    for filename in filenames:
        filepath = os.path.join(outputDirectory, filename)
        with open(filepath) as f:
            data = json.load(f)

        # Sorts the articles based on weighted_average in descending order
        sorted_articles = sorted(data['articles'], key=lambda x: x['weighted_average'], reverse=True)

        # Updates the articles in the data
        data['articles'] = sorted_articles

        # Writes the updated JSON back to the file with pretty formatting
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        # Prints the success message with the full absolute path
        absolutePath = os.path.abspath(filepath)
        print(f"JSON file sorted successfully: {absolutePath}")

    print("Sorting of JSON files completed successfully.")


    ########################################################
    # same operations but for the datase with already 1k articles and categories

def sortJSONsDescWeights_1k():
    # Gets the current script directory
    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    # Gets the parent directory (one level above)
    parentDirectory = os.path.abspath(os.path.join(currentDirectory, os.pardir))

    # Specifies the directory name
    outputDirectory = os.path.join(parentDirectory, "1kPlots")

    # Checks if the directory exists
    if not os.path.exists(outputDirectory):
        print(f"Error: Directory 'output Files' not found in {parentDirectory}")
        return

    # Specifies the list of filenames to process
    filenames = [
        "30clash70_angular_1k.json",
        "30clash70_cosine_1k.json",
        "30clash70_euclidean_1k.json",
        "30clash70_minkowski_1k.json"
    ]

    # Checks if all required files exist
    missingFiles = []
    for filename in filenames:
        filepath = os.path.join(outputDirectory, filename)
        if not os.path.exists(filepath):
            missingFiles.append(filename)

    if missingFiles:
        print(f"Error: The following files are missing in the '1kPlots' directory:")
        for filename in missingFiles:
            print(filename)
        return

    # Processes the existing files
    for filename in filenames:
        filepath = os.path.join(outputDirectory, filename)
        with open(filepath) as f:
            data = json.load(f)

        # Sorts the articles based on weighted_average in descending order
        sortedArticles = sorted(data['articles'], key=lambda x: x['weighted_average'], reverse=True)

        # Updates the articles in the data
        data['articles'] = sortedArticles

        # Writes the updated JSON back to the file with pretty formatting
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

        # Prints the success message with the full absolute path
        absolutePath = os.path.abspath(filepath)
        print(f"JSON file sorted successfully: {absolutePath}")

    print("Sorting of JSON files completed successfully.")