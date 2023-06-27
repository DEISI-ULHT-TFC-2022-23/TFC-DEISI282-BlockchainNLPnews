# README

## About the project

Welcome to this exciting project that aims to tackle the notorious problem of fake news! Our mission is to create a Python program that combines the power of Blockchain-structured DB and distance metric algorithms to fight against misinformation.

Picture this: we're building a fortress of reliable and trustworthy articles, safeguarded within a Blockchain-structured DB. It's like a high-security vault where no modifications are allowed without the secret code (any attempts will trigger a full-scale re-download of the database, so don't even think about it!).

To ensure the accuracy of our distance metric algorithms (**Cosine Similarity, Euclidean Distance, Angular Distance, Minkowski Distance**), we've even created a super fun manual classification system for the stored articles. Yes, it's a bit old-school, but I couldn't whip up an automatic one in time. You'll get to see the algorithms' performance in interactive plots and peek at the results in nifty `.json` files.

But wait, there's more! The real test of our project lies in your hands. You get to insert an article from another source, written in a completely different way, and see what comes out from the other side. Will our program find the perfect match? It's like finding a needle in a haystack

### How the project works

Behold, the heart and soul of our project: two mighty databases:

-  **The blockchain DB, the sanctuary of article information (title, URL, date, article body, and more).**

-  **The classifiers DB, the guardian of article categories. It's where we store the user-assigned categories and our cleverly calculated categories. **
**(both powered by MongoDB).**

Now, for the main attractions of our project:

1.  **The Scraping**: We'll ask you how many articles you'd like us to scrape from the [AP News](https://apnews.com/) website. We'll go undercover and perform cleaning operations, sifting out duplicates, cleaning up text, and bidding farewell to non-English articles. The chosen articles will then be added to the Blockchain DB, with all the hashing operations of a blockchain in full swing.
2.  **The Categories:** You'll have the honor of assigning one of ten categories to each article. Once that's done, our project will split the articles into two sets (30% for testing, 70% for training). We'll employ the mighty SBERT to shrink the text to a compact 768 dimensions. Then, we unleash the 4 distance metric algorithms to determine the most fitting category for each article. We will display the results in 5 interactive plots showcasing the accuracy of these algorithms. And don't worry, we've saved the results in snazzy `.json` files for your inspection.

3.  **The Article Clash**: You can insert the body of your own chosen article and see what comes out from the other end. But remember, make sure to copy the article body to your clipboard. We'll keep asking if you have more parts of the article body to insert. **Sadly, we couldn't automate this process perfectly (it's harder than it sounds!)**. Once you've presented the entire article, we'll display the URL of the page that our calculations deem as the most similar to your article. It's like uncovering a hidden gem.

## **How to install**

To get this project up and running, follow these 4 simple steps:

1. download the project from this repository, extract it to your PC

2. Start your favorite IDE. Mine happens to be Microsoft Visual Studio,  and open the project folder inside it

3. Make sure you have Python installed on your PC. I recommend Python 3.11. Head over to [python.org](https://www.python.org/downloads/release/python-3110/) and grab the installer. We didn't test this project with other Python versions, so let's stick to the recommended one for now.

4. MongoDB is your trusty sidekick. Install MongoDB on your system and make sure it's up and running. There are plenty of guides on the internet to help you with that. I followed this YouTube video: [MongoDB Setup Made Easy](https://www.youtube.com/watch?v=gB6WLkSrtJk).

Now, let's move on to the installation process. Open your terminal and navigate to the project folder. Then, execute the following lines of code:
```
python -m venv Blockhouse

.\Blockhouse\Scripts\activate

pip install -r requirements.txt`
```
We are creating a cozy virtual environment called "Blockhouse" to host all the necessary files. Then, we invite all the necessary requirements to join us.

Almost there! The final step is to open the project Folder in your IDE and start the code from the Main.py file. **Remember, starting the code from any other file will cause chaos and confusion. Stick to the Main.py file for a smooth experience.**

### Overview of the main menu of the project

Now, let's take a quick tour of the project's main menu. Each option is does a few things you should familiarize yourself with:

1.  **Scrap ApNews to add articles to the Blockchain DB**: You get to choose how many articles you want to extract from ApNews, and our program will clean them up, remove duplicates, and store them in the Blockchain.

2.  **Ask user to insert the body of an article and compare it with all the stored articles**: We'll ask you to insert the body of an article, bit by bit, and our program will compare it with all the stored articles. We'll use our secret distance metric algorithms to find the best match for you. And guess what? We'll save the results in .json files so you can analyze them later.

3.  **Divides the articles into 2 sets, 30% is testing articles, 70% is training articles sets and calculates new categories for 30% of the articles and plots them**: We'll divide the articles into two sets, one for testing and one for training. Then, we'll use our magical algorithms to calculate new categories for the testing articles. And then we'll create interactive plots to show you the results.

4.  **Test the program with an already classified DB with 1k articles**: We have a pre-categorized Blockchain DB with 1137 articles ready to go. Just sit back, and watch it do all the work for you. We'll display the plots for you and the .json files with the results will be ready for you at the end.

5.  **Delete entire blockchain DB and stored articles (if it exists)**:  It's a reset button that wipes out the entire Blockchain DB and all the stored articles.

6.  **Delete the entire DB that has the articles categories (if it exists)**: Made a mistake? No worries, we can fix it. This option allows you to delete the DB that contains the categories of each article. Just be careful not to create any inconsistencies.

7.  **Delete a block from the blockchain (testing purposes)**: With this option, you can delete any valid block from the Blockchain DB. It's like being a hacker, but with good intentions. Just remember, deleting a block triggers a re-download of the Blockchain DB.

8.  **Print the number of articles stored on each BD**: Want to see some numbers? This option prints the number of elements in each DB.

9.  **Export blockchain to JSON File (if it exists, only for viewing purposes)**: You can export the current Blockchain DB to a mesmerizing .json file. Do whatever you want with it, it's all yours to explore.

10.  **Export classifiers DB to JSON (if it exists, only for viewing purposes)**: This option lets you export the current Classifiers DB to a splendid .json file. Take a peek into the categories.

11.  **Backup Blockchain DB and classifiers BD to project folder**: Use this option to make a backup of your current Blockchain DB and Classifiers DB to the project folder. This allows you to take mess up with the databases without having any real consequences.

12.  **Restores saved Blockchain DB and classifiers BD to this system**: Made a mess? This option restores the saved backup files from option '11' and loads them into a proper mongo database.

## What You Can and Can't Do
This project wasn't designed for commercial purposes, so I kindly request that you handle its contents with care. While you have the power to move or delete any of the .json files, tampering with other files might have unforseen consequences.

## Known Issues
1. It's not really a big deal, but more like a party of terminal clutter. Thanks to Matplotlib's quirks and the way those 5 plots were cooked up, if you start tickling them too much, the terminal might get a bit grumpy and spew out errors like the ones you see in the image below:

--Plot Errors--

Don't worry, though. The program won't throw a tantrum and crash on you. It will keep working as expected. I tried my best to silence those warning messages, but so far no luck

2. "No import detected for langdetect" -> When you fire up the program for the first time, it might whine about not finding the 'langdetect' library. 
Blame it on the IDE's cache mischief and the library's dance with the virtual environment. But here's the secret trick: if you run the program a second time right after that error, it should magically start working like a charm and take you straight to the main menu. Check out the image below to see what happens during the first run, courtesy of the pesky 'langdetect' library:
![langdetect](https://github.com/FilipeCacho/BlockchainNLP/blob/main/readME%20images/langdetect.png)
