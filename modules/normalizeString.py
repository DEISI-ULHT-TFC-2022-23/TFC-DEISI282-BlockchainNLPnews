import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
import string
import re

# Check if the required NLTK data is downloaded, and if not, download it
nltk.download('punkt')

def normalizeString(blockchainTextArticle):
    # Remove URLs
    blockchainTextArticle = re.sub(r'http\S+|www\S+', '', blockchainTextArticle)

    # Sentence segmentation
    text = nltk.sent_tokenize(blockchainTextArticle)

    normalizedText = []
    for sentence in text:
        # Remove special characters
        sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)

        # Tokenize the sentence
        tokens = nltk.word_tokenize(sentence)

        # Remove single-character tokens
        tokens = [token for token in tokens if len(token) > 1]

        # Remove repeated characters
        tokens = [re.sub(r'(.)\1+', r'\1', token) for token in tokens]

        # Remove consecutive digits
        tokens = [re.sub(r'\d+', '0', token) for token in tokens]

        # Lowercase the tokens
        tokens = [token.lower() for token in tokens]

        # Remove stopwords and punctuations
        stopWords = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stopWords and token not in string.punctuation]

        # Remove non-alphanumeric characters
        tokens = [token for token in tokens if re.match('^[a-zA-Z0-9]+$', token)]

        # Remove numeric tokens
        tokens = [token for token in tokens if not token.isdigit()]

        # Stem the tokens using PorterStemmer
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]

        # Lemmatize the tokens using WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

        # Join the normalized tokens into a string
        normalized_text = " ".join(tokens)

        normalizedText.append(normalized_text)

    # Join the normalized sentences into a string
    normalizedarticle = " ".join(normalizedText)

    return normalizedarticle