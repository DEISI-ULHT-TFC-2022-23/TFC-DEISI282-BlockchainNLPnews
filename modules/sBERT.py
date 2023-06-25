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
from modules.sortJSONsDescWeights import sortJSONsDescWeights


# Calculate angular distances between vectors
def angular_distances(X, Y):
    # Normalize X and Y
    X_norm = X / np.linalg.norm(X, axis=1)[:, np.newaxis]
    Y_norm = Y / np.linalg.norm(Y, axis=1)[:, np.newaxis]

    # Compute dot product between normalized X and Y
    dot_product = np.dot(X_norm, Y_norm.T)

    # Clip dot product values to avoid invalid values for arccos
    dot_product = np.clip(dot_product, -1.0, 1.0)

    # Compute angular distances
    angular_dists = np.arccos(dot_product)

    return angular_dists

def classifyArticles():

    try:
        # Connect to the MongoDB database and retrieve the chain collection
        client = MongoClient("mongodb://localhost:27017/")
        db = client["blockchain_db"]
        collection = db["chain"]

        # Connect to the mongoDB classifiers
        dbCat = client["classifiers_db"]
        collectionCat = dbCat["categories"]

        # Load the SBERT model
        sbert_model = SentenceTransformer('sentence-transformers/bert-base-nli-mean-tokens')

        # Create lists to store the embeddings, titles, and categories
        embeddings = []
        titles = []
        categories = []

        # Fetch the documents from the classifiers collection
        classification_cursor = collectionCat.find()

        for document in classification_cursor:
            # Fetch the article link and body from the classifiers collection
            article_link = document['article_link']
            article_title = document['article_title']


            # Fetch the corresponding normalized article body from the blockchain DB to pass it to SBERT
            article = collection.find_one({'article_link': article_link, 'article_title': article_title})
            if article:
                
                normalized_body = article['normalized_body']

                # Pass the article body text to SBERT and reduce it to 768 dimensions
                article_embedding = sbert_model.encode(normalized_body, convert_to_tensor=True, show_progress_bar=True, device='cpu')

                article_embedding = article_embedding.numpy().tolist()

                # Replace the original article body text with the embedding
                document['article_body'] = article_embedding

                embeddings.append(article_embedding)
                titles.append(article_title)
                categories.append(document['category_text'])

        # Print the number of embeddings
        print(f"Number of embeddings: {len(embeddings)}")

        # Plot the UMAP embeddings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Suppress the warnings
            embeddings_with_data = [{'embedding': e, 'category': c, 'title': t} for e, c, t in zip(embeddings, categories, titles)]
            category_texts = [doc['category'] for doc in embeddings_with_data]

            # Create a set to store unique categories
            unique_categories = set(category_texts)
            sorted_unique_categories = sorted(list(unique_categories))
            num_categories = len(unique_categories)
            colors = mpl.cm.get_cmap('tab10', lut=num_categories)
            color_map = {category: colors(i) for i, category in enumerate(sorted_unique_categories)}

            umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umap_embeddings = umap_model.fit_transform(embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            category_colors = [color_map[category] for category in category_texts]

            # Plot the scatter plot
            scatter = ax.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], color=category_colors, alpha=0.5)

            # Create a legend with the category labels
            legend_elements = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in color_map.items()]
            ax.legend(handles=legend_elements)

            # Configure cursor annotations
            try:
                cursor = mplcursors.cursor(scatter)
                cursor.connect("add", lambda sel: sel.annotation.set_text(embeddings_with_data[sel.target.index]['title']))

                ax.set_title('UMAP Embeddings with Categories')

                with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                    plt.show()

            except Exception as e:
                print("An error occurred:", str(e))

            # Check if the output file exists, create it if it doesn't
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output Files")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "30clash70.json")

            # Randomly select 70% of the embeddings with data and their categories
            num_samples = len(embeddings_with_data)
            train_size = int(num_samples * 0.7)
            train_indices = set(random.sample(range(num_samples), train_size))
            train_embeddings = [embeddings_with_data[i]['embedding'] for i in train_indices]
            train_categories = [embeddings_with_data[i]['category'] for i in train_indices]
            train_titles = [embeddings_with_data[i]['title'] for i in train_indices]

            # Get the remaining 30% of the embeddings with data
            test_indices = list(set(range(num_samples)) - train_indices)
            test_embeddings = [embeddings_with_data[i]['embedding'] for i in test_indices]
            test_categories = [embeddings_with_data[i]['category'] for i in test_indices]
            test_titles = [embeddings_with_data[i]['title'] for i in test_indices]

            # Calculate cosine similarity between test_embeddings and train_embeddings
            cosine_similarities = cosine_similarity(test_embeddings, train_embeddings)

            # Calculate Euclidean distances between test_embeddings and train_embeddings
            euclidean_dists = euclidean_distances(test_embeddings, train_embeddings)

            # Calculate angular distances between test_embeddings and train_embeddings
            angular_dists = angular_distances(np.array(test_embeddings), np.array(train_embeddings))

            # Create a dictionary to map category labels to numerical values
            category_mapping = {
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
            train_categories_numerical = [category_mapping[category] for category in train_categories]

            # Create variables to count hits and misses
            cosine_hits = 0
            cosine_misses = 0
            euclidean_hits = 0
            euclidean_misses = 0
            angular_hits = 0
            angular_misses = 0

            # Create a list to store the cosine similarity results
            cosine_results = []

            # Find the most similar articles for each article in the test set using cosine similarity
            for i, similarities in enumerate(cosine_similarities):
                top_indices = np.argsort(similarities)[::-1][:5]  # Get the indices of the top 5 most similar articles
                top_categories = np.array([train_categories_numerical[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                top_similarities = np.array([similarities[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on similarity values
                top_weights = np.array([2 * similarity if similarity >= 0.8 else 0.5 * similarity for similarity in top_similarities], dtype=np.float64)

                # Calculate the weighted average of top categories
                weighted_average = np.average(top_categories, weights=top_weights)

                # Find the new category based on the weighted average
                rounded_average = round(weighted_average)
                new_category = max(category_mapping, key=lambda x: category_mapping[x])  # Initialize with the highest category
                for category, value in category_mapping.items():
                    if value == rounded_average:
                        new_category = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": test_titles[i],
                    "original_category": test_categories[i],  # Fetch the original category from test_categories
                    "weighted_average": weighted_average,
                    "new_category": new_category
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    cosine_hits += 1
                else:
                    cosine_misses += 1

                # Append the dictionary to the list of results
                cosine_results.append(result)

            # Create a list to store the Euclidean distance results
            euclidean_results = []

            # Find the most similar articles for each article in the test set using Euclidean distance
            for i, distances in enumerate(euclidean_dists):
                top_indices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                top_categories = np.array([train_categories_numerical[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                top_distances = np.array([distances[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                top_weights = np.array([2 / (distance + 1e-6) for distance in top_distances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weighted_average = np.average(top_categories, weights=top_weights)

                # Find the new category based on the weighted average
                rounded_average = round(weighted_average)
                new_category = max(category_mapping, key=lambda x: category_mapping[x])  # Initialize with the highest category
                for category, value in category_mapping.items():
                    if value == rounded_average:
                        new_category = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": test_titles[i],
                    "original_category": test_categories[i],  # Fetch the original category from test_categories
                    "weighted_average": weighted_average,
                    "new_category": new_category
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    euclidean_hits += 1
                else:
                    euclidean_misses += 1

                # Append the dictionary to the list of results
                euclidean_results.append(result)

            # Create a list to store the angular distance results
            angular_results = []

            # Find the most similar articles for each article in the test set using angular distance
            for i, distances in enumerate(angular_dists):
                top_indices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                top_categories = np.array([train_categories_numerical[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                top_distances = np.array([distances[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                top_weights = np.array([2 / (distance + 1e-6) for distance in top_distances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weighted_average = np.average(top_categories, weights=top_weights)

                # Find the new category based on the weighted average
                rounded_average = round(weighted_average)
                new_category = max(category_mapping, key=lambda x: category_mapping[x])  # Initialize with the highest category
                for category, value in category_mapping.items():
                    if value == rounded_average:
                        new_category = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": test_titles[i],
                    "original_category": test_categories[i],  # Fetch the original category from test_categories
                    "weighted_average": weighted_average,
                    "new_category": new_category
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    angular_hits += 1
                else:
                    angular_misses += 1

                # Append the dictionary to the list of results
                angular_results.append(result)

            # Create an overall results dictionary to include hits and misses along with the cosine similarity results
            cosine_overall_results = {
                "total_hits": cosine_hits,
                "total_misses": cosine_misses,
                "articles": cosine_results
            }

            # Calculate the weighted average accuracy for cosine similarity
            cosine_accuracy = cosine_hits / (cosine_hits + cosine_misses) * 100

            # Print the weighted average accuracy for cosine similarity
            print(f"\nWeighted Average Accuracy (Cosine Similarity): {cosine_accuracy:.2f}%")

            # Plot the UMAP embeddings with categories for cosine similarity
            cosine_new_categories = [result['new_category'] for result in cosine_results]
            embeddings_with_data = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(test_embeddings, cosine_new_categories, test_titles)]
            category_texts = [doc['category'] for doc in embeddings_with_data]

            # Create a set to store unique categories
            unique_categories = set(category_texts)
            sorted_unique_categories = sorted(list(unique_categories))
            num_categories = len(unique_categories)
            colors = mpl.cm.get_cmap('tab10', num_categories)
            color_map = {category: colors(i) for i, category in enumerate(sorted_unique_categories)}

            umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umap_embeddings = umap_model.fit_transform(test_embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            category_colors = [color_map[category] for category in category_texts]

            # Plot the scatter plot
            scatter = ax.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], color=category_colors, alpha=0.5)

            # Create a legend with the category labels
            legend_elements = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in color_map.items()]
            ax.legend(handles=legend_elements)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddings_with_data[idx]['title']
                original_category = test_categories[idx]
                weighted_average = cosine_results[idx]['weighted_average']
                new_category = cosine_results[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Cosine Similarity)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Calculate the weighted average accuracy for Euclidean distance
            euclidean_accuracy = euclidean_hits / (euclidean_hits + euclidean_misses) * 100

            # Print the weighted average accuracy for Euclidean distance
            print(f"\nWeighted Average Accuracy (Euclidean Distance): {euclidean_accuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Euclidean distance
            euclidean_new_categories = [result['new_category'] for result in euclidean_results]
            embeddings_with_data = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(test_embeddings, euclidean_new_categories, test_titles)]
            category_texts = [doc['category'] for doc in embeddings_with_data]

            # Create a set to store unique categories
            unique_categories = set(category_texts)
            sorted_unique_categories = sorted(list(unique_categories))
            num_categories = len(unique_categories)
            colors = mpl.cm.get_cmap('tab10', num_categories)
            color_map = {category: colors(i) for i, category in enumerate(sorted_unique_categories)}

            umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umap_embeddings = umap_model.fit_transform(test_embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            category_colors = [color_map[category] for category in category_texts]

            # Plot the scatter plot
            scatter = ax.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], color=category_colors, alpha=0.5)

            # Create a legend with the category labels
            legend_elements = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in color_map.items()]
            ax.legend(handles=legend_elements)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddings_with_data[idx]['title']
                original_category = test_categories[idx]
                weighted_average = euclidean_results[idx]['weighted_average']
                new_category = euclidean_results[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Euclidean Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Calculate the weighted average accuracy for Angular distance
            angular_accuracy = angular_hits / (angular_hits + angular_misses) * 100

            # Print the weighted average accuracy for Angular distance
            print(f"\nWeighted Average Accuracy (Angular Distance): {angular_accuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Angular distance
            angular_new_categories = [result['new_category'] for result in angular_results]
            embeddings_with_data = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(test_embeddings, angular_new_categories, test_titles)]
            category_texts = [doc['category'] for doc in embeddings_with_data]

            # Create a set to store unique categories
            unique_categories = set(category_texts)
            sorted_unique_categories = sorted(list(unique_categories))
            num_categories = len(unique_categories)
            colors = mpl.cm.get_cmap('tab10', num_categories)
            color_map = {category: colors(i) for i, category in enumerate(sorted_unique_categories)}

            umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umap_embeddings = umap_model.fit_transform(test_embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            category_colors = [color_map[category] for category in category_texts]

            # Plot the scatter plot
            scatter = ax.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], color=category_colors, alpha=0.5)

            # Create a legend with the category labels
            legend_elements = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in color_map.items()]
            ax.legend(handles=legend_elements)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddings_with_data[idx]['title']
                original_category = test_categories[idx]
                weighted_average = angular_results[idx]['weighted_average']
                new_category = angular_results[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Angular Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Check if the output file exists, create it if it doesn't
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output Files")
            os.makedirs(output_dir, exist_ok=True)
            output_file_cosine = os.path.join(output_dir, "30clash70_cosine.json")
            output_file_euclidean = os.path.join(output_dir, "30clash70_euclidean.json")
            output_file_angular = os.path.join(output_dir, "30clash70_angular.json")

            # Create an overall results dictionary for cosine similarity
            cosine_overall_results = {
                "total_hits": cosine_hits,
                "total_misses": cosine_misses,
                "accuracy": f"{cosine_accuracy:.2f}%",
                "articles": cosine_results
            }

            # Write the cosine similarity results to the JSON file
            with open(output_file_cosine, 'w') as f:
                json.dump(cosine_overall_results, f, indent=4)

            # Create an overall results dictionary for Euclidean distance
            euclidean_overall_results = {
                "total_hits": euclidean_hits,
                "total_misses": euclidean_misses,
                "accuracy": f"{euclidean_accuracy:.2f}%",
                "articles": euclidean_results
            }

            # Write the Euclidean distance results to the JSON file
            with open(output_file_euclidean, 'w') as f:
                json.dump(euclidean_overall_results, f, indent=4)

            # Create an overall results dictionary for Angular distance
            angular_overall_results = {
                "total_hits": angular_hits,
                "total_misses": angular_misses,
                "accuracy": f"{angular_accuracy:.2f}%",
                "articles": angular_results
            }

            # Write the Angular distance results to the JSON file
            with open(output_file_angular, 'w') as f:
                json.dump(angular_overall_results, f, indent=4)

            # Calculate Minkowski distances between test_embeddings and train_embeddings
            minkowski_dists = []
            minkowski_hits = 0
            minkowski_misses = 0
            for test_embedding in test_embeddings:
                distances = [minkowski(test_embedding, train_embedding, p=2) for train_embedding in train_embeddings]
                minkowski_dists.append(distances)

            # Create a list to store the Minkowski distance results
            minkowski_results = []

            # Find the most similar articles for each article in the test set using Minkowski distance
            for i, distances in enumerate(minkowski_dists):
                top_indices = np.argsort(distances)[:5]  # Get the indices of the top 5 most similar articles
                top_categories = np.array([train_categories_numerical[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64
                top_distances = np.array([distances[idx] for idx in top_indices], dtype=np.float64)  # Convert to NumPy array with dtype=np.float64

                # Create weights based on distance values
                top_weights = np.array([2 / (distance + 1e-6) for distance in top_distances], dtype=np.float64)

                # Calculate the weighted average of top categories
                weighted_average = np.average(top_categories, weights=top_weights)

                # Find the new category based on the weighted average
                rounded_average = round(weighted_average)
                new_category = max(category_mapping, key=lambda x: category_mapping[x])  # Initialize with the highest category
                for category, value in category_mapping.items():
                    if value == rounded_average:
                        new_category = category
                        break

                # Create a dictionary to store the result for this test article
                result = {
                    "test_article_title": test_titles[i],
                    "original_category": test_categories[i],  # Fetch the original category from test_categories
                    "weighted_average": weighted_average,
                    "new_category": new_category
                }

                # Compare the original category with the new category and update the hit/miss counts
                if result["original_category"] == result["new_category"]:
                    minkowski_hits += 1
                else:
                    minkowski_misses += 1

                # Append the dictionary to the list of results
                minkowski_results.append(result)

            minkowski_accuracy = minkowski_hits / (minkowski_hits + minkowski_misses) * 100
            
            # Create an overall results dictionary for Minkowski distance
            minkowski_overall_results = {
                "total_hits": minkowski_hits,
                "total_misses": minkowski_misses,
                "accuracy": f"{minkowski_accuracy:.2f}%",
                "articles": minkowski_results
            }

            # Write the Minkowski distance results to the JSON file
            output_file_minkowski = os.path.join(output_dir, "30clash70_minkowski.json")
            with open(output_file_minkowski, 'w') as f:
                json.dump(minkowski_overall_results, f, indent=4)

            # Print the weighted average accuracy for Minkowski distance
            
            print(f"\nWeighted Average Accuracy (Minkowski Distance): {minkowski_accuracy:.2f}%")

            # Plot the UMAP embeddings with categories for Minkowski distance
            minkowski_new_categories = [result['new_category'] for result in minkowski_results]
            embeddings_with_data = [{'embedding': e, 'category': nc, 'title': t} for e, nc, t in zip(test_embeddings, minkowski_new_categories, test_titles)]
            category_texts = [doc['category'] for doc in embeddings_with_data]

            # Create a set to store unique categories
            unique_categories = set(category_texts)
            sorted_unique_categories = sorted(list(unique_categories))
            num_categories = len(unique_categories)
            colors = mpl.cm.get_cmap('tab10', num_categories)
            color_map = {category: colors(i) for i, category in enumerate(sorted_unique_categories)}

            umap_model = UMAP(n_neighbors=5, min_dist=0.3, n_components=2, metric='cosine', random_state=42)
            umap_embeddings = umap_model.fit_transform(test_embeddings)

            fig, ax = plt.subplots(figsize=(10, 10))

            scatter = None  # Initialize scatter plot variable

            # Convert the category values to color values
            category_colors = [color_map[category] for category in category_texts]

            # Plot the scatter plot
            scatter = ax.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], color=category_colors, alpha=0.5)

            # Create a legend with the category labels
            legend_elements = [mpl.lines.Line2D([0], [0], marker='o', color='w', label=category, markerfacecolor=color, markersize=10)
                            for category, color in color_map.items()]
            ax.legend(handles=legend_elements)

            # Configure cursor annotations
            def annotation_text(sel):
                idx = sel.target.index
                title = embeddings_with_data[idx]['title']
                original_category = test_categories[idx]
                weighted_average = minkowski_results[idx]['weighted_average']
                new_category = minkowski_results[idx]['new_category']
                return f"{title}\nOriginal Category: {original_category}\nWeighted Average: {weighted_average}\nNew Category: {new_category}"

            cursor = mplcursors.cursor(scatter)
            cursor.connect("add", lambda sel: sel.annotation.set_text(annotation_text(sel)))

            ax.set_title('UMAP Embeddings with Categories (Minkowski Distance)')

            with mpl.rc_context(rc={'figure.max_open_warning': 0}):
                plt.show()

            # Update the paths to the output files
            output_file_cosine = os.path.relpath(output_file_cosine)
            output_file_euclidean = os.path.relpath(output_file_euclidean)
            output_file_angular = os.path.relpath(output_file_angular)
            output_file_minkowski = os.path.relpath(output_file_minkowski)
            os.system('cls')
            print(f"\nCosine similarity results saved to: {output_file_cosine}")
            print(f"Euclidean distance results saved to: {output_file_euclidean}")
            print(f"Angular distance results saved to: {output_file_angular}")
            print(f"Minkowski distance results saved to: {output_file_minkowski}")

            ##order JSONs weighted categories by descending order
            sortJSONsDescWeights()

            input("Press ENTER to continue")
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Error: Could not connect to the MongoDB server. Please ensure the server is running.")
        sys.exit(1)

    except pymongo.errors.OperationFailure:
        print("Error: The blockchain_db database does not exist or is not available.")
        sys.exit(1)


def sBERT():

    os.system('cls')
    
    print("For this code to properly work the it needs to match every article stored in the Blockchain DB with the content of the classifiers BD")
    print("If for any reason the number of articles in the Blockchain DB is not equal to the number of articles in the Classifiers BD, the program will not continue")
    print("(if you have any remaining articles you need to classify you can press 'n' when the program asks you next if you already classified all articles)")
    print("If for any reason you added new content to the Blockchain DB that you didn't classify yet, be sure to do it or those articles won't show up on the plot \n")
    print ("You can press on the dots on the plots to get more information about the article it represents, the program will show a total of 5 plots and will continue after you close the current open plot \n")
    input("Press ENTER to continue \n")

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
    else:
        print("Could not establish a connection with the blockchain DB or collection does not exist")
        print ("Scrap news articles from the website using option '1' of the main menu to load information into the blockchain DB \n")
        input("Press ENTER to continue")
        return

    #########################################################################################################
    # Connect to the mongoDB classifiers, connects if exists and creates if it doesn't exist
    dbCat = client["classifiers_db"]
    collectionCat = dbCat["categories"]

    # Check if the database and collection exist and if the connection is successful
    if dbCat.command("ping")["ok"] == 1 and "categories" in dbCat.list_collection_names():
        print("Connection to the categories collection successful")
        time.sleep(0.7)
    else:
        print("Could not establish a connection with the categories collection or collection does not exist")

        # Create the collection if it doesn't exist
        dbCat.create_collection("categories")
        collectionCat = dbCat["categories"]
        print("Categories collection created")
        time.sleep(0.7)

    #########################################################################################################
    # Check if the data is already classified

    # count the number of records in the classifiers BD
    existingClassifiersRecords = collectionCat.count_documents({})

    # total number of articles in the blockchain DB, -1 is because of the gensis block
    existingChainRecords = max(collection.count_documents({}) - 1, 0)


    # count the number of remaining articles to classify
    totalArticles = max(collection.count_documents({}) - 1, 0)


    while True:
        already_classified = input("Did you already classified all the articles (including new article added to the Blockchain)? (y/n) ")
        if already_classified.lower() == "y":
            print ("\n")
            # Check if the classifiers db is empty
            if not bool(collectionCat.find_one()):
                print("The classifiers database is empty. Please classify the data before continuing.")
                input("Press ENTER to continue")
                return
            
            if existingClassifiersRecords <= 19:
                print("UMAP breaks with less than 20 articles due to density. Please classify the data or extract more articles before continuing.")
                input("Press ENTER to continue")
                return

            elif existingClassifiersRecords != existingChainRecords:
                print("The total number of articles in the classifiers BD (", existingClassifiersRecords, ") does not match the total number of articles in the blockchain BD (", existingChainRecords,")")
                print("You can either: \n")
                print(" - Classify the remaining articles by selecting 'n' on option '3' of the main menu; \n")
                print ("- Drop the classifiers BD using option '6' on the main menu and classify the existing articles in the blockchain DB again \n")
                input("Press ENTER to continue")
                return


            classifyArticles()  # Call the function to use classifiers and plot embeddings
            return

        elif already_classified.lower() == "n":
            # Initialize a counter variabl
            counter = 0
            print("\n")

            if existingChainRecords<=19 :
                print("UMAP breaks with less than 20 articles due to density. Please classify the data or extract more articles before continuing.")
                input("Press ENTER to continue")
                return
            
            elif existingClassifiersRecords>existingChainRecords :
                print("The total number of articles in the classifiers BD (", existingClassifiersRecords, ") exceeds the total number of articles in the blockchain BD (", existingChainRecords, ")")
                print("This will cause inconsistencies, please drop the classifiers BD and classify the articles from the start")
                input("Press ENTER to continue")
                return

            # Iterate over articles in the blockchain db
            for block in collection.find(no_cursor_timeout=True):
                if "article_link" in block and "article_body" in block:
                    if block["article_title"] == "I'm the genesis block":
                        continue  # Skip the genesis block

                    # Check if the article exists in the classifications database
                    existing_classification = collectionCat.find_one({'article_link': block['article_link'], 'article_title': block['article_title']})
                    if existing_classification:
                        totalArticles -= 1
                        continue  # Skip the article if it already exists in the classifications database

                    # Increment the counter for non-genesis blocks
                    counter += 1

                    # Get user input for the category
                    os.system('cls')
                    print(f"Article link: {block['article_link']}")
                    print(f"Article title: {block['article_title']}")
                    print("Article body:")
                    print(f"{block['article_body']}\n")
                    print(f"Number of articles remaining: {counter}/{totalArticles}")

                    # Display categories
                    print("\nCategories:")
                    print("1. Politics/Government")
                    print("2. Business/Economy")
                    print("3. Science/Technology")
                    print("4. Health/Medicine")
                    print("5. Environment/Nature")
                    print("6. Culture/Education")
                    print("7. Sports/Recreation")
                    print("8. Lottery Numbers")
                    print("9. Crime/Law")
                    print("10. International/Global Affairs \n")

                    # Define a dictionary to map category numbers to category texts
                    category_mapping = {
                        "1": "Politics/Government",
                        "2": "Business/Economy",
                        "3": "Science/Technology",
                        "4": "Health/Medicine",
                        "5": "Environment/Nature",
                        "6": "Culture/Education",
                        "7": "Sports/Recreation",
                        "8": "Lottery Numbers",
                        "9": "Crime/Law",
                        "10": "International/Global Affairs"
                    }

                    # Prompt user to enter a category number
                    while True:
                        category_input = input("Enter a category number for the article: " )
                        print("\n")

                        # Check if input is valid (i.e. a number from 1 to 10)
                        if category_input.isdigit() and 1 <= int(category_input) <= 10:
                            category_number = int(category_input)
                            category_text = category_mapping[str(category_number)]

                            # Store the article_link, article_title, category number, and category text in the categories collection
                            post = {
                                "article_link": block["article_link"],
                                "article_title": block["article_title"],
                                "category_number": category_number,
                                "category_text": category_text
                            }
                            collectionCat.insert_one(post)
                            break
                        else:
                            print("Invalid input. Please enter a number from 1 to 10.")

            os.system('cls')
            print("All articles are already classified, on the main menu select option '3' and select 'y' to see the plots ")
            input("Press ENTER to continue")
            return

        else:
            print("Invalid input. Please enter 'y' or 'n'.")