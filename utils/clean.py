import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from io import StringIO # Keep StringIO imported as it's used internally for reading
from tqdm import tqdm

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# --- NLTK Downloads ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()

# --- Text Preprocessing Functions ---

def remove_html_tags(text):
    """Removes HTML tags from a string."""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def remove_punctuation(text):
    """Removes punctuation from a string."""
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
    """
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = remove_urls(text)
    text = remove_html_tags(text)
    text = remove_punctuation(text)
    
    if apply_lemmatization:
        text = tokenize_and_lemmatize(text)
        
    text = text.strip()
    return text

# --- Data Ingestion and Overall Cleaning Function ---

# MODIFIED: Accepts file_object (StringIO) and file_type string
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
            # Use file_object directly with pandas
            df = pd.read_csv(file_object)
            if 'feedback_text' not in df.columns:
                raise ValueError("CSV file must contain a 'feedback_text' column.")
            feedback_texts = df['feedback_text'].astype(str).tolist()
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}. Ensure it's correctly formatted with 'feedback_text' column.")
    
    elif file_type == 'json':
        try:
            # Use json.load directly with file_object
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
            # Read line by line from the file_object's content
            feedback_texts = [line.strip() for line in file_object if line.strip()]
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {e}. Ensure it's plain text with one feedback per line.")
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Please upload a CSV, JSON, or TXT file.")

    # Apply preprocessing
    cleaned_feedback = []
    # Use tqdm if you have a lot of feedback for a progress bar effect
    for text in tqdm(feedback_texts, desc="Cleaning Feedback"):
        cleaned_feedback.append(preprocess_text(text, apply_lemmatization))
    
    cleaned_feedback = [f for f in cleaned_feedback if f]

    if not cleaned_feedback:
        raise ValueError("No valid feedback text found after cleaning. Please check your file content.")

    return cleaned_feedback