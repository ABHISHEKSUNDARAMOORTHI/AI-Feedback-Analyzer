import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st
import pandas as pd
from collections import Counter

def plot_sentiment_distribution(sentiments: list[str]):
    """
    Generates and displays a bar chart of sentiment distribution.

    Args:
        sentiments (list[str]): A list of sentiment labels (e.g., "Positive", "Negative", "Neutral").
    """
    if not sentiments:
        st.warning("No sentiment data available for visualization.")
        return

    sentiment_counts = pd.Series(sentiments).value_counts()
    
    # Define colors for better visualization
    colors = {
        'Positive': 'skyblue',
        'Negative': 'salmon',
        'Neutral': 'lightgray',
        'Error': 'darkred' # In case there are errors
    }
    # Map counts to corresponding colors
    sentiment_colors = [colors.get(s, 'gray') for s in sentiment_counts.index]

    fig, ax = plt.subplots(figsize=(8, 5))
    sentiment_counts.plot(kind='bar', ax=ax, color=sentiment_colors)
    
    ax.set_title('Sentiment Distribution', fontsize=16)
    ax.set_xlabel('Sentiment', fontsize=12)
    ax.set_ylabel('Number of Feedbacks', fontsize=12)
    ax.tick_params(axis='x', rotation=0) # Keep x-axis labels horizontal
    
    # Add count labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%d')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free up memory


def generate_word_cloud(topics: list[str]):
    """
    Generates and displays a word cloud from a list of topics.

    Args:
        topics (list[str]): A list of extracted topic strings.
    """
    if not topics:
        st.warning("No topic data available for word cloud generation.")
        return

    # Join all topics into a single string
    topics_text = " ".join(topics)

    if not topics_text.strip():
        st.warning("No valid text found for word cloud after cleaning topics.")
        return

    # Create a WordCloud object
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white', # Standard for word clouds, can be changed
        collocations=False, # Set to False to prevent repeating words from phrases
        min_font_size=10,
        max_words=100 # Limit to top 100 words/topics
    ).generate(topics_text)

    # Display the generated image:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') # Do not show axes
    ax.set_title('Most Frequent Topics', fontsize=16)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig) # Close the figure to free up memory


# Example of how you might use it (for testing visualize.py independently)
if __name__ == '__main__':
    st.title("Visualization Test")
    
    sample_sentiments = ["Positive", "Positive", "Negative", "Neutral", "Positive", "Negative", "Positive", "Neutral"]
    st.subheader("Sentiment Distribution Example:")
    plot_sentiment_distribution(sample_sentiments)

    sample_topics = [
        "shipping", "product quality", "customer service", "pricing",
        "shipping", "product quality", "delivery", "app performance",
        "customer service", "pricing", "returns", "product quality",
        "shipping", "ease of use", "customer service"
    ]
    st.subheader("Word Cloud Example:")
    generate_word_cloud(sample_topics)