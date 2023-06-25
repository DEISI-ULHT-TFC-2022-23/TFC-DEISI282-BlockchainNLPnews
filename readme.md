# About the project

The goal of this project was to create a prototype of a Python program that could be used to help combat fake news by using a combination of a Blockchain-structured DB and distance metric algorithms that measure the similarity between vectors or data points in a given space.

The goal was to build a database of articles from reliable and trusted sources and store them in a Blockchain-structured DB. This database, due to its nature, cannot be modified without full access to the code (any attempts will force a full re-download of the database).

To verify the accuracy of the distance metric algorithms (cosine similarity, Euclidean distance, angular distance, Minkowski distance) used in the project, I've built tools to allow the manual classification (yes, manual; there was not enough time to build an automatic classification system) of the stored articles. Then, the user is able to see the accuracy of all the algorithms in interactive plots, and the results are stored in `.json` files that the user can inspect.

Finally, the most important test is to allow the user to insert an article of their choosing from another source about a topic they know exists in the database, written in a completely different way, and see if the program returns the expected article.

## How the project works

The entire project revolves around 2 databases:

- The blockchain DB, that stores all the articles' information (title, URL, date, article body, etc.)
- The classifiers DB, that stores all the information about the categories of each article. It stores the user's assigned category and the newly calculated category (more info below) (both of these DBs work using MongoDB)

The project has 3 main functionalities:

1. Asks the user how many articles they want to scrape from the [AP News](https://apnews.com/) website, performs cleaning operations like removing duplicates, cleaning the text, removing articles not in English, etc. Adds those articles to the blockchain DB and performs the required hashing operations of a blockchain.

2. On the main menu, the user can choose to plot all the stored articles in the blockchain DB. But first, the user is required to assign 1 of 10 categories to each stored article. Then, the project will divide the articles into 2 sets (30% for testing, 70% for training), and it uses SBERT to reduce the text to 768 dimensions. After that, it will attempt to calculate the most fitting category for each article using the 4 distance metric algorithms and plot the results. It also saves those results into `.json` files. The goal of these plots is to help the user visualize the accuracy of the distance metric algorithms.

3. Allows the user to insert the body of an article of their own choice and compare it to the articles stored in the blockchain DB. When this option is selected, the user is warned that they must copy the article body to their clipboard because that is where the program will extract from. Next, it will ask the user if there are more parts of the article body they want to insert from the clipboard, and it will keep asking this until the user answers "No". Ideally, this process would be automatic, but it is impossible to correctly analyze and extract only the article body from any webpage without bringing a lot of irrelevant text. Therefore, this task will unfortunately have to be left to the user. Once the user inputs the entire article, the program will display the URL of the page that, according to its calculations, is the most similar to the user's article. The ideal scenario is that the result of this operation is that both pages are about the same topic (if the Blockchain DB has such an article stored, of course).

The project's main menu has several options, and the functionality of each one will be briefly described below:
