import os
import json
from sklearn.metrics.pairwise import cosine_similarity

def compareUserArticleWithDB(userArticleRawText, userNormalizedArticle, embeddings, titles, articleLinks, articleBodies):

    # Replace '\r\n' with '\n', split the text into a list of paragraphs, and filter out empty strings
    userArticleParagraphs = list(filter(None, userArticleRawText.replace('\r\n', '\n').split('\n')))

    # calculates cosine similarity between user article and the embeddings
    cosineSimilarities = cosine_similarity([userNormalizedArticle], embeddings)[0]

    results = []

    # adds user article raw text to the results
    userResult = {
        "user_article_paragraphs": userArticleParagraphs
    }
    results.append(userResult)

    # compares the user article with each article in the embeddings
    for i, similarity in enumerate(cosineSimilarities):
        article_result = {
            "article_link": articleLinks[i],
            "article_title": titles[i],
            "cosine_similarity": similarity
        }
        results.append(article_result)

    # sorts the results by cosine similarity in descending order
    results = sorted(results, key=lambda x: x.get("cosine_similarity", 0), reverse=True)

    # checks if user article result exists in the results
    if userResult in results:
        # Move the user article to the top of the list
        results.insert(0, results.pop(results.index(userResult)))

    top5SimilarArticles = results[:5]

    # gets the current directory
    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    # Goes up one level
    projectFolderPath = os.path.dirname(currentDirectory)

    # creates the path to the "output Files" folder
    outputFolderPath = os.path.join(projectFolderPath, "output Files")

    # creates the "output Files" folder if it doesn't exist
    os.makedirs(outputFolderPath, exist_ok=True)

    # creates the file path by concatenating the output folder path with the filename
    outputFilepath = os.path.join(outputFolderPath, "comparison_results.json")

    # saves the results to the .json file in the output folder
    with open(outputFilepath, "w", encoding="utf-8") as file:
        json.dump(top5SimilarArticles, file, indent=4, ensure_ascii=False)

    print("Comparison results saved to 'output Files/comparison_results.json'")
    input("Press ENTER to continue")