# README

## About the project

Welcome to this exciting project that aims to tackle the notorious problem of fake news! Our mission is to create a Python program that combines the power of Blockchain-structured DB and distance metric algorithms to fight against misinformation.

Picture this: we're building a fortress of reliable and trustworthy articles, safeguarded within a Blockchain-structured DB. It's like a high-security vault where no modifications are allowed without the secret code (any attempts will trigger a full-scale re-download of the database, so don't even think about it!).

To ensure the accuracy of our distance metric algorithms (**Cosine similarity, Euclidean distance, angular distance, Minkowski distance**), we've even created a super fun manual classification system for the stored articles. Yes, it's a bit old-school, but we couldn't whip up an automatic one in time (oops!). You'll get to see the algorithms' performance in interactive plots and peek at the results in nifty `.json` files.

But wait, there's more! The real test of our project lies in your hands. You get to insert an article from another source, written in a completely different way, and witness the magic unfold. Will our program find the perfect match from our treasure trove? It's like finding a needle in a haystack, but with a touch of technological wizardry!

### How the project works

Behold, the heart and soul of our project: two mighty databases:

**- The blockchain DB, the sanctuary of article information (title, URL, date, article body, and more).
- The classifiers DB, the guardian of article categories. It's where we store the user-assigned categories and our cleverly calculated categories (both powered by MongoDB).**

Now, brace yourself for the main attractions of our project:

1. **The Scraping Extravaganza**: We'll ask you how many articles you'd like us to scrape from the [AP News](https://apnews.com/) website. We'll go undercover and perform cleaning operations, sifting out duplicates, cleaning up text, and bidding farewell to non-English articles. These golden nuggets will then be added to the blockchain DB, with all the hashing operations of a blockchain in full swing. Impressive, right?

2. **The Category Carnival**: Step right up and witness the grand plot! You'll have the honor of assigning one of ten categories to each article. Once that's done, our project will split the articles into two sets (30% for testing, 70% for training). We'll employ the mighty SBERT to shrink the text to a compact 768 dimensions. Then, behold as we unleash the 4 distance metric algorithms to determine the most fitting category for each article. Prepare to be dazzled by interactive plots showcasing the accuracy of these algorithms. And don't worry, we've saved the results in snazzy `.json` files for your inspection.

3. **The Article Adventure**: This is where you become the hero! You can insert the body of your own chosen article and witness the clash of the titans. But remember, before entering the realm, make sure to copy the article body to your clipboard. It's like the magical incantation that fuels our program. We'll keep asking if you have more parts of the article body to insert, just like a treasure hunt. **Sadly, we couldn't automate this process perfectly (it's harder than it sounds!)**. Once you've presented the entire article, brace yourself for the grand reveal. We'll display the URL of the page that our calculations deem as the most similar to your article. It's like uncovering a hidden gem, just for you!

The main menu of our project is teeming with excitement and options. So, prepare to be entertained and embark on an extraordinary journey!