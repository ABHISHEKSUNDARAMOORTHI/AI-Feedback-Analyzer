import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core import exceptions
import time
from dotenv import load_dotenv

load_dotenv()

# Configure API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- Function to get a supported model name ---
def get_supported_model(preferred_models=['gemini-1.5-flash', 'gemini-1.0-pro'], fallback_model='gemini-1.0-pro'):
    """
    Attempts to find a supported Gemini model for generateContent,
    preferring a list of models, then falling back to a default.
    """
    print("Checking available models...")
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        print(f"Models supporting generateContent: {available_models}")

        for p_model in preferred_models:
            # The model names returned by list_models include "models/" prefix
            full_model_name = f"models/{p_model}" 
            if full_model_name in available_models:
                print(f"Using preferred model: {p_model}")
                return p_model # Return the short name for genai.GenerativeModel
        
        # If preferred models are not found, try the fallback
        full_fallback_name = f"models/{fallback_model}"
        if full_fallback_name in available_models:
            print(f"Preferred models not found. Falling back to: {fallback_model}")
            return fallback_model
        
        # If no suitable model is found, raise an error
        raise ValueError(f"No suitable Gemini model found. Available: {available_models}. Please check your model names or API access.")

    except Exception as e:
        print(f"Error listing models: {e}")
        print(f"Attempting to proceed with fallback model '{fallback_model}' (might still fail).")
        return fallback_model # Fallback if listing fails entirely


# Initialize gemini_model using the helper function
model_to_use = get_supported_model(preferred_models=['gemini-1.5-flash', 'gemini-1.0-pro'])

try:
    gemini_model = genai.GenerativeModel(model_to_use)
    # REMOVED 'timeout' argument here
    gemini_model.generate_content("test", safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
    })
    print(f"Successfully initialized model: {model_to_use}")
except Exception as e:
    print(f"Failed to initialize or use '{model_to_use}': {e}. This could be a temporary issue or a model problem.")
    print("Consider checking your internet connection, API key, and Google AI Studio quotas.")
    # Fallback to a very generic, basic model if all else fails, or raise a critical error
    try:
        gemini_model = genai.GenerativeModel('gemini-1.0-pro')
        # REMOVED 'timeout' argument here
        gemini_model.generate_content("test", safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE
        })
        print("Successfully fell back to gemini-1.0-pro.")
    except Exception as fallback_e:
        raise RuntimeError(f"Critical Error: Could not initialize any Gemini model. Last attempt failed with: {fallback_e}")


# --- Helper Function for Robust API Calls with Exponential Backoff ---
def make_gemini_call_with_retry(prompt, model_instance, max_retries=7, initial_delay=1.0):
    """
    Makes a Gemini API call with exponential backoff for quota/rate limit (429) errors.

    Args:
        prompt (str): The prompt to send to the Gemini model.
        model_instance: The configured Gemini GenerativeModel instance.
        max_retries (int): Maximum number of retry attempts.
        initial_delay (float): Initial delay in seconds before the first retry.

    Returns:
        str: The generated text response, or an error message if all retries fail.
    """
    retries = 0
    delay = initial_delay
    while retries < max_retries:
        try:
            response = model_instance.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            # Check for valid response text
            if response and response.text:
                return response.text
            else:
                print(f"AI response was empty or blocked for input. Prompt feedback: {response.prompt_feedback}")
                return "AI response was empty or blocked for this input, possibly due to safety settings."

        except exceptions.ResourceExhausted as e:
            retries += 1
            if retries < max_retries:
                print(f"Quota/Rate Limit Exceeded (429). Retrying in {delay:.2f} seconds... (Attempt {retries}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                return f"Failed to get response after {max_retries} retries due to quota/rate limit: {e}"
        except Exception as e:
            print(f"An unexpected API error occurred during generate_content call: {e}")
            return f"An unexpected API error occurred: {e}"
    
    return "Failed to get response after multiple retries (unknown reason)."


# --- Sentiment Analysis ---
def get_sentiment(feedback):
    prompt = f"Analyze the sentiment of the following customer feedback: '{feedback}'. Respond with only one word: Positive, Negative, or Neutral."
    return make_gemini_call_with_retry(prompt, gemini_model)

# --- Topic Extraction ---
def extract_topics(feedback):
    prompt = f"Extract 2 to 5 main topics or keywords from the following customer feedback: '{feedback}'. Respond as a comma-separated list. Example: 'delivery, speed, tracking, app issues'. If no topics are found, respond with 'no topics'."
    raw_topics = make_gemini_call_with_retry(prompt, gemini_model)
    
    if raw_topics and raw_topics != "no topics" and not raw_topics.startswith("An unexpected API error occurred:") and not raw_topics.startswith("Failed to get response after"):
        return [topic.strip() for topic in raw_topics.split(',') if topic.strip()]
    return []

# --- Overall Summary Generation ---
def generate_overall_summary(feedback_list):
    summary_feedback_sample = feedback_list[:100]
    
    if not summary_feedback_sample:
        return "No feedback provided to generate a summary."

    feedback_text = "\n".join(summary_feedback_sample)
    
    overall_prompt = f"""
    You are an AI assistant specialized in analyzing customer feedback.
    Generate a comprehensive summary of the following customer feedback entries.
    Provide the summary in the following structured Markdown format:

    ## Overall Feedback Summary

    ### 1. General Sentiment Distribution
    - Briefly describe the overall sentiment (e.g., predominantly positive, mixed, largely negative).

    ### 2. Key Positive Themes and Highlights
    - Identify and summarize recurring positive aspects.
    - Provide 1-2 example quotes or themes if possible.

    ### 3. Key Negative Issues and Areas for Improvement
    - Identify and summarize recurring negative issues or complaints.
    - Provide 1-2 example quotes or themes if possible.

    ### 4. Actionable Suggestions and Recommendations
    - Based on the feedback, provide 2-3 concrete, actionable suggestions for the business to improve.

    ### Customer Feedback Entries:
    {feedback_text}
    """
    return make_gemini_call_with_retry(overall_prompt, gemini_model)

# --- NEW: Function for general chat interactions ---
def get_chat_response(chat_prompt):
    """
    Generates a response for chat-like interactions using the Gemini model
    with built-in retry logic.
    """
    return make_gemini_call_with_retry(chat_prompt, gemini_model)