import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from io import StringIO
from tqdm import tqdm

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- NLTK Downloads (ensure these run only once, e.g., at app startup or first import) ---
# Check if data is already downloaded to avoid repeated downloads
try:
    nltk.data.find('tokenizers/punkt')
except LookupError: # Corrected from nltk.downloader.DownloadError
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError: # Corrected from nltk.downloader.DownloadError
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError: # Corrected from nltk.downloader.DownloadError
    nltk.download('omw-1.4', quiet=True)

# Initialize lemmatizer globally to avoid re-initializing in a loop if used often
lemmatizer = WordNetLemmatizer()

# --- Text Preprocessing Functions ---

def remove_html_tags(text):
    """Removes HTML tags from a string."""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def remove_punctuation(text):
    """Removes punctuation from a string."""
    # This regex keeps alphanumeric characters and whitespace
    return re.sub(r'[^\w\s]', '', text)

def remove_urls(text):
    """Removes URLs from a string."""
    return re.sub(r'http\S+|www.\S+', '', text)

def tokenize_and_lemmatize(text):
    """Tokenizes text and applies lemmatization."""
    tokens = word_tokenize(text)
    lemmas = [lemmatizer.lemmatize(token) for token in tokens]
    return " ".join(lemmas)

def preprocess_text(text, apply_lemmatization=False):
    """
    Applies a series of preprocessing steps to a single string.

    Args:
        text (str): The input text string.
        apply_lemmatization (bool): Whether to apply tokenization and lemmatization.

    Returns:
        str: The cleaned and optionally lemmatized text.
    """
    if not isinstance(text, str):
        return "" # Handle non-string inputs (e.g., NaN from pandas)
    
    text = text.lower()
    text = remove_urls(text)
    text = remove_html_tags(text)
    text = remove_punctuation(text)
    
    if apply_lemmatization:
        text = tokenize_and_lemmatize(text)
        
    text = text.strip() # Remove leading/trailing whitespace
    return text

# --- Data Ingestion and Overall Cleaning Function ---

def ingest_and_clean_data(file_object, file_type: str, apply_lemmatization=False):
    """
    Ingests data from a file-like object and applies cleaning.

    Args:
        file_object: A file-like object (e.g., io.StringIO) containing the file content.
        file_type (str): The type of the file ('csv', 'json', 'txt').
        apply_lemmatization (bool): Whether to apply tokenization and lemmatization.

    Returns:
        list: A list of cleaned feedback strings.
    """
    feedback_texts = []

    if file_type == 'csv':
        try:
            df = pd.read_csv(file_object)
            if 'feedback_text' not in df.columns:
                raise ValueError("CSV file must contain a 'feedback_text' column.")
            feedback_texts = df['feedback_text'].astype(str).tolist()
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}. Ensure it's correctly formatted with 'feedback_text' column.")
    
    elif file_type == 'json':
        try:
            data = json.load(file_object)
            if isinstance(data, list):
                feedback_texts = [item.get('feedback', '') for item in data if isinstance(item, dict)]
            else:
                raise ValueError("JSON file must be a list of objects, each with a 'feedback' field.")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file format.")
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}. Ensure it's a list of objects with a 'feedback' field.")

    elif file_type == 'txt':
        try:
            feedback_texts = [line.strip() for line in file_object if line.strip()]
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {e}. Ensure it's plain text with one feedback per line.")
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Please upload a CSV, JSON, or TXT file.")

    cleaned_feedback = []
    # tqdm is for local development progress bars, might not show in Streamlit Cloud logs
    for text in tqdm(feedback_texts, desc="Cleaning Feedback"): 
        cleaned_feedback.append(preprocess_text(text, apply_lemmatization))
    
    cleaned_feedback = [f for f in cleaned_feedback if f]

    if not cleaned_feedback:
        raise ValueError("No valid feedback text found after cleaning. Please check your file content.")

    return cleaned_feedback
