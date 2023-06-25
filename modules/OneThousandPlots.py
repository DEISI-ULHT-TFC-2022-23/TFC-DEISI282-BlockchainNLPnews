import os
import json
import random
import warnings
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.lines import Line2D
import pymongo
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import sys
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import minkowski
from umap import UMAP
import time
import warnings
import matplotlib as mpl
from modules.sortJSONsDescWeights import sortJSONsDescWeights_1k
from modules.DbOps import restore1kBlockchain, restore1kClassifiers

# Calculate angular distances between vectors
def angularDistances(X, Y):
    # Normalize X and Y
    xNormalized = X / np.linalg.norm(X, axis=1)[:, np.newaxis]
    y_Normalized = Y / np.linalg.norm(Y, axis=1)[:, np.newaxis]

    # Compute dot product between normalized X and Y
    product = np.dot(xNormalized, y_Normalized.T)

    # Clip dot product values to avoid invalid values for arccos
    product = np.clip(product, -1.0, 1.0)

    # Compute angular distances
    angularDist = np.arccos(product)

    return angularDist

def aThousandPlots():

    # if for any reason the restoring of either of the BD's fail the program will return to main
    if not restore1kClassifiers() or not restore1kBlockchain():
        return

    print ("You can press on the dots on the plots to get more information about the article it represents, the program will show a total of 5 plots and will continue after you close the current open plot \n")
    input("Press ENTER to continue \n")

    try:
        # Connect to the MongoDB database and retrieve the chain collection
        client = MongoClient("mongodb://localhost:27017/")
        db = client["blockchain_1k"]
        collection = db["chain1k"]

        # Connect to the mongoDB classifiers
        dbCat = client["classifiers_1k"]
        collectionCat = dbCat["categories1k"]

        # Load the SBERT model
        sbertModel = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens')

        embeddings = []
        titles = []
        categories = []

        # Fetch the documents from the classifiers collection
        cursor = collectionCat.find()

        for document in cursor:
            # Fetch the article link and body from the classifiers collection
            article_link = document['article_link']
            article_title = document['article_title']

            # Fetch the corresponding normalized article body from the blockchain DB to pass it to SBERT
            article = collection.find_one({'article_link': article_link, 'article_title': article_title})
            if article:
                
                normalizedBody = article['normalized_body']

                # Pass the article body text to SBERT and reduce it to 768 dimensions
                articleEmbedding = sbertModel.encode(normalizedBody, convert_to_tensor=True, show_progress_bar=True, device='cpu')

                articleEmbedding = articleEmbedding.numpy().tolist()

                # Replace the original article body text with the embedding
                document['article_body'] = articleEmbedding

                embeddings.append(articleEmbedding)
                titles.append(article_title)
                categories.append(document['category_text'])

        # Print the number of embeddings
        print(f"Number of embeddings: {len(embeddings)}")

        # Plot the UMAP embeddings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress the warnings
            embeddingsData = [{'embedding': e, 'category': c, 'title': t} for e, c, t in zip(embeddings, categories, titles)]
            textCategories = [doc['category'] for doc in embeddingsData]

            # Create a set to store unique categories
            uniqueCategories = set(textCategories)
            sortedUniqueCategories = sorted(list(uniqueCategories))
            numCategories = len(uniqueCategories)
            colors = mpl.cm.get_cmap('tab10', lut=numCategories)
            rainbowMap = {category: colors(i) for i, category in enumerate(sortedUniqueCategories)}

            umapModel = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umapEmbeddings = umapModel.fit_transform(embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            categoryColors = [rainbowMap[category] for category in textCategories]

            # Plot the scatter plot
            scatter = ax.scatter(umapEmbeddings[:, 0], umapEmbeddings[:, 1], color=categoryColors, alpha=0.5)

            # Create a legend with the category labels
            legendText = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in rainbowMap.items()]
            ax.legend(handles=legendText)

            # Configure cursor annotations
            try:
                cursor = mplcursors.cursor(scatter)
                cursor.connect("add", lambda sel: sel.annotation.set_text(embeddingsData[sel.target.index]['title']))

                ax.set_title('UMAP Embeddings with Categories')

                with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                    plt.show()

            except Exception as e:
                print("An error occurred:", str(e))

            # Check if the output file exists, create it if it doesn't
            output_Directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "1kPlots")
            os.makedirs(output_Directory, exist_ok=True)
            outputFile = os.path.join(output_Directory, "30clash70_1k.json")

            # Randomly select 70% of the embeddings with data and their categories
            numSamples = len(embeddingsData)
            trainSize = int(numSamples * 0.7)
            trainIndices = set(random.sample(range(numSamples), trainSize))
            trainEmbeddings = [embeddingsData[i]['embedding'] for i in trainIndices]
            trainCategories = [embeddingsData[i]['category'] for i in trainIndices]
            trainTitles = [embeddingsData[i]['title'] for i in trainIndices]

            # Get the remaining 30% of the embeddings with data
            testIndices = list(set(range(numSamples)) - trainIndices)
            testEmbeddings = [embeddingsData[i]['embedding'] for i in testIndices]
            testCategories = [embeddingsData[i]['category'] for i in testIndices]
            testTitles = [embeddingsData[i]['title'] for i in testIndices]

            # Calculate cosine similarity between test_embeddings and train_embeddings
            cosineSimilarity = cosine_similarity(testEmbeddings, trainEmbeddings)

            # Calculate Euclidean distances between test_embeddings and train_embeddings
            euclideanDistance = euclidean_distances(testEmbeddings, trainEmbeddings)

            # Calculate angular distances between test_embeddings and train_embeddings
            angularDistance = angularDistances(np.array(testEmbeddings), np.array(trainEmbeddings))

            # Create a dictionary to map category labels to numerical values
            categoryMap = {
                "Politics/Government": 1,
                "Business/Economy": 2,
                "Science/Technology": 3,
                "Health/Medicine": 4,
                "Environment/Nature": 5,
                "Culture/Education": 6,
                "Sports/Recreation": 7,
                "Lottery Numbers": 8,
                "Crime/Law": 9,
                "International/Global Affairs": 10
            }

            # Convert train_categories to numerical values using the category_mapping dictionary
            trainCategoriesNum = [categoryMap[category] for category in trainCategories]

            # Create variables to count hits and misses
            cosineHits = 0
            cosineMisses = 0
            euclideanHits = 0
            euclideanMisses = 0
            angularHits = 0
            angularMisses = 0

            # Create a list to store the cosine similarity results
            cosineResults = []

            # Find the most similar articles for each article in the test set using cosine similarity
            for i, similarities in enumerate(cosineSimilarity):
                topIndices = np.argsort(similarities)[::-1][:5]  # Get the indices of the top 5 most similar articles
                topCategories = np.array([trainCategoriesNum[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                topSimilarities = np.array([similarities[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on similarity values
                topWeights = np.array([2 * similarity if similarity >= 0.8 else 0.5 * similarity for similarity in topSimilarities], dtype=np.float64)

                # Calculate the weighted average of top categories
                weightedAverage = np.average(topCategories, weights=topWeights)

                # Find the new category based on the weighted average
                roundedAverage = round(weightedAverage)
                newCategories = max(categoryMap, key=lambda x: categoryMap[x])  # Initialize with the highest category
                for category, value in categoryMap.items():
                    if value == roundedAverage:
                        newCategories = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": testTitles[i],
                    "original_category": testCategories[i],  # Fetch the original category from test_categories
                    "weighted_average": weightedAverage,
                    "new_category": newCategories
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    cosineHits += 1
                else:
                    cosineMisses += 1

                # Append the dictionary to the list of results
                cosineResults.append(result)

            # Create a list to store the Euclidean distance results
            euclideanResults = []

            # Find the most similar articles for each article in the test set using Euclidean distance
            for i, distances in enumerate(euclideanDistance):
                topIndices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                topCategories = np.array([trainCategoriesNum[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                topDistances = np.array([distances[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                topWeights = np.array([2 / (distance + 1e-6) for distance in topDistances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weightedAverage = np.average(topCategories, weights=topWeights)

                # Find the new category based on the weighted average
                roundedAverage = round(weightedAverage)
                newCategories = max(categoryMap, key=lambda x: categoryMap[x])  # Initialize with the highest category
                for category, value in categoryMap.items():
                    if value == roundedAverage:
                        newCategories = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": testTitles[i],
                    "original_category": testCategories[i],  # Fetch the original category from test_categories
                    "weighted_average": weightedAverage,
                    "new_category": newCategories
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    euclideanHits += 1
                else:
                    euclideanMisses += 1

                # Append the dictionary to the list of results
                euclideanResults.append(result)

            # Create a list to store the angular distance results
            angularResults = []

            # Find the most similar articles for each article in the test set using angular distance
            for i, distances in enumerate(angularDistance):
                topIndices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                topCategories = np.array([trainCategoriesNum[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                topDistances = np.array([distances[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                topWeights = np.array([2 / (distance + 1e-6) for distance in topDistances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weightedAverage = np.average(topCategories, weights=topWeights)

                # Find the new category based on the weighted average
                roundedAverage = round(weightedAverage)
                newCategories = max(categoryMap, key=lambda x: categoryMap[x])  # Initialize with the highest category
                for category, value in categoryMap.items():
                    if value == roundedAverage:
                        newCategories = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": testTitles[i],
                    "original_category": testCategories[i],  # Fetch the original category from test_categories
                    "weighted_average": weightedAverage,
                    "new_category": newCategories
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    angularHits += 1
                else:
                    angularMisses += 1

                # Append the dictionary to the list of results
                angularResults.append(result)

            # Create an overall results dictionary to include hits and misses along with the cosine similarity results
            finalCosineResults = {
                "total_hits": cosineHits,
                "total_misses": cosineMisses,
                "articles": cosineResults
            }

            # Calculate the weighted average accuracy for cosine similarity
            cosineAccuracy = cosineHits / (cosineHits + cosineMisses) * 100

            # Print the weighted average accuracy for cosine similarity
            print(f"\nWeighted Average Accuracy (Cosine Similarity): {cosineAccuracy:.2f}%")

            # Plot the UMAP embeddings with categories for cosine similarity
            newCosineCategories = [result['new_category'] for result in cosineResults]
            embeddingsData = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(testEmbeddings, newCosineCategories, testTitles)]
            textCategories = [doc['category'] for doc in embeddingsData]

            # Create a set to store unique categories
            uniqueCategories = set(textCategories)
            sortedUniqueCategories = sorted(list(uniqueCategories))
            numCategories = len(uniqueCategories)
            colors = mpl.cm.get_cmap('tab10', numCategories)
            rainbowMap = {category: colors(i) for i, category in enumerate(sortedUniqueCategories)}

            umapModel = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umapEmbeddings = umapModel.fit_transform(testEmbeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            categoryColors = [rainbowMap[category] for category in textCategories]

            # Plot the scatter plot
            scatter = ax.scatter(umapEmbeddings[:, 0], umapEmbeddings[:, 1], color=categoryColors, alpha=0.5)

            # Create a legend with the category labels
            legendText = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in rainbowMap.items()]
            ax.legend(handles=legendText)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddingsData[idx]['title']
                originalCategory = testCategories[idx]
                weightedAverage = cosineResults[idx]['weighted_average']
                newCategory = cosineResults[idx]['new_category']
                return f"{title}\nOriginal Category: {originalCategory}\nWeighted Average: {weightedAverage}\nNew Category: {newCategory}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Cosine Similarity)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Calculate the weighted average accuracy for Euclidean distance
            euclideanAccuracy = euclideanHits / (euclideanHits + euclideanMisses) * 100

            # Print the weighted average accuracy for Euclidean distance
            print(f"\nWeighted Average Accuracy (Euclidean Distance): {euclideanAccuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Euclidean distance
            euclideanNewCategory = [result['new_category'] for result in euclideanResults]
            embeddingsData = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(testEmbeddings, euclideanNewCategory, testTitles)]
            textCategories = [doc['category'] for doc in embeddingsData]

            # Create a set to store unique categories
            uniqueCategories = set(textCategories)
            sortedUniqueCategories = sorted(list(uniqueCategories))
            numCategories = len(uniqueCategories)
            colors = mpl.cm.get_cmap('tab10', numCategories)
            rainbowMap = {category: colors(i) for i, category in enumerate(sortedUniqueCategories)}

            umapModel = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umapEmbeddings = umapModel.fit_transform(testEmbeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            categoryColors = [rainbowMap[category] for category in textCategories]

            # Plot the scatter plot
            scatter = ax.scatter(umapEmbeddings[:, 0], umapEmbeddings[:, 1], color=categoryColors, alpha=0.5)

            # Create a legend with the category labels
            legendText = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in rainbowMap.items()]
            ax.legend(handles=legendText)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddingsData[idx]['title']
                original_category = testCategories[idx]
                weighted_average = euclideanResults[idx]['weighted_average']
                new_category = euclideanResults[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Euclidean Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Calculate the weighted average accuracy for Angular distance
            angularAccuracy = angularHits / (angularHits + angularMisses) * 100

            # Print the weighted average accuracy for Angular distance
            print(f"\nWeighted Average Accuracy (Angular Distance): {angularAccuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Angular distance
            angularNewCategory = [result['new_category'] for result in angularResults]
            embeddingsData = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(testEmbeddings, angularNewCategory, testTitles)]
            textCategories = [doc['category'] for doc in embeddingsData]

            # Create a set to store unique categories
            uniqueCategories = set(textCategories)
            sortedUniqueCategories = sorted(list(uniqueCategories))
            numCategories = len(uniqueCategories)
            colors = mpl.cm.get_cmap('tab10', numCategories)
            rainbowMap = {category: colors(i) for i, category in enumerate(sortedUniqueCategories)}

            umapModel = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umapEmbeddings = umapModel.fit_transform(testEmbeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            categoryColors = [rainbowMap[category] for category in textCategories]

            # Plot the scatter plot
            scatter = ax.scatter(umapEmbeddings[:, 0], umapEmbeddings[:, 1], color=categoryColors, alpha=0.5)

            # Create a legend with the category labels
            legendText = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in rainbowMap.items()]
            ax.legend(handles=legendText)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddingsData[idx]['title']
                originalcategory = testCategories[idx]
                weightedAverage = angularResults[idx]['weighted_average']
                newCategory = angularResults[idx]['new_category']
                return f"{title}\nOriginal Category: {originalcategory}\nWeighted Average: {weightedAverage}\nNew Category: {newCategory}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Angular Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Check if the output file exists, create it if it doesn't
            output_Directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "1kPlots")
            os.makedirs(output_Directory, exist_ok=True)
            cosineOutputFile = os.path.join(output_Directory, "30clash70_cosine_1k.json")
            eucledeanOutputFile = os.path.join(output_Directory, "30clash70_euclidean_1k.json")
            angularOutputFile = os.path.join(output_Directory, "30clash70_angular_1k.json")

            # Create an overall results dictionary for cosine similarity
            finalCosineResults = {
                "total_hits": cosineHits,
                "total_misses": cosineMisses,
                "accuracy": f"{cosineAccuracy:.2f}%",
                "articles": cosineResults
            }

            # Write the cosine similarity results to the JSON file
            with open(cosineOutputFile, 'w') as f:
                json.dump(finalCosineResults, f, indent=4)

            # Create an overall results dictionary for Euclidean distance
            euclideanFinalResults = {
                "total_hits": euclideanHits,
                "total_misses": euclideanMisses,
                "accuracy": f"{euclideanAccuracy:.2f}%",
                "articles": euclideanResults
            }

            # Write the Euclidean distance results to the JSON file
            with open(eucledeanOutputFile, 'w') as f:
                json.dump(euclideanFinalResults, f, indent=4)

            # Create an overall results dictionary for Angular distance
            angularFinalResults = {
                "total_hits": angularHits,
                "total_misses": angularMisses,
                "accuracy": f"{angularAccuracy:.2f}%",
                "articles": angularResults
            }

            # Write the Angular distance results to the JSON file
            with open(angularOutputFile, 'w') as f:
                json.dump(angularFinalResults, f, indent=4)

            # Calculate Minkowski distances between test_embeddings and train_embeddings
            minkowskiDistance = []
            minkowskiHits = 0
            minkowskiMisses = 0
            for testingEmbeddings in testEmbeddings:
                distances = [minkowski(testingEmbeddings, train_embedding, p=2) for train_embedding in trainEmbeddings]
                minkowskiDistance.append(distances)

            # Create a list to store the Minkowski distance results
            minkowskiResults = []

            # Find the most similar articles for each article in the test set using Minkowski distance
            for i, distances in enumerate(minkowskiDistance):
                topIndices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                topCategories = np.array([trainCategoriesNum[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                topDistances = np.array([distances[idx] for idx in topIndices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                topWeights = np.array([2 / (distance + 1e-6) for distance in topDistances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weightedAverage = np.average(topCategories, weights=topWeights)

                # Find the new category based on the weighted average
                roundedAverage = round(weightedAverage)
                newCategories = max(categoryMap, key=lambda x: categoryMap[x])  # Initialize with the highest category
                for category, value in categoryMap.items():
                    if value == roundedAverage:
                        newCategories = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": testTitles[i],
                    "original_category": testCategories[i],  # Fetch the original category from test_categories
                    "weighted_average": weightedAverage,
                    "new_category": newCategories
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    minkowskiHits += 1
                else:
                    minkowskiMisses += 1

                # Append the dictionary to the list of results
                minkowskiResults.append(result)

            minkowskyAccuracy = minkowskiHits / (minkowskiHits + minkowskiMisses) * 100
            
            # Create an overall results dictionary for Minkowski distance
            minkowskiFinalResults = {
                "total_hits": minkowskiHits,
                "total_misses": minkowskiMisses,
                "accuracy": f"{minkowskyAccuracy:.2f}%",
                "articles": minkowskiResults
            }

            # Write the Minkowski distance results to the JSON file
            minkowskiOutputFile = os.path.join(output_Directory, "30clash70_minkowski_1k.json")
            with open(minkowskiOutputFile, 'w') as f:
                json.dump(minkowskiFinalResults, f, indent=4)

            # Print the weighted average accuracy for Minkowski distance
            
            print(f"\nWeighted Average Accuracy (Minkowski Distance): {minkowskyAccuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Minkowski distance
            minkowskiNewCategories= [result['new_category'] for result in minkowskiResults]
            embeddingsData = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(testEmbeddings, minkowskiNewCategories, testTitles)]
            textCategories = [doc['category'] for doc in embeddingsData]

            # Create a set to store unique categories
            uniqueCategories = set(textCategories)
            sortedUniqueCategories = sorted(list(uniqueCategories))
            numCategories = len(uniqueCategories)
            colors = mpl.cm.get_cmap('tab10', numCategories)
            rainbowMap = {category: colors(i) for i, category in enumerate(sortedUniqueCategories)}

            umapModel = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umapEmbeddings = umapModel.fit_transform(testEmbeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            categoryColors = [rainbowMap[category] for category in textCategories]

            # Plot the scatter plot
            scatter = ax.scatter(umapEmbeddings[:, 0], umapEmbeddings[:, 1], color=categoryColors, alpha=0.5)

            # Create a legend with the category labels
            legendText = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in rainbowMap.items()]
            ax.legend(handles=legendText)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddingsData[idx]['title']
                original_category = testCategories[idx]
                weighted_average = minkowskiResults[idx]['weighted_average']
                new_category = minkowskiResults[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Minkowski Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Update the paths to the output files
            cosineOutputFile = os.path.relpath(cosineOutputFile)
            eucledeanOutputFile = os.path.relpath(eucledeanOutputFile)
            angularOutputFile = os.path.relpath(angularOutputFile)
            minkowskiOutputFile = os.path.relpath(minkowskiOutputFile)
            os.system('cls')
            print(f"\nCosine similarity results saved to: {cosineOutputFile}")
            print(f"Euclidean distance results saved to: {eucledeanOutputFile}")
            print(f"Angular distance results saved to: {angularOutputFile}")
            print(f"Minkowski distance results saved to: {minkowskiOutputFile}")

            ##order JSONs weighted categories by descending order
            sortJSONsDescWeights_1k()

            input("Press ENTER to continue")
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: Could not connect to the MongoDB server. Please ensure the server is running.")
        sys.exit(1)

    except pymongo.errors.OperationFailure:
        print("Error: The blockchain_db database does not exist or is not available.")
        sys.exit(1)