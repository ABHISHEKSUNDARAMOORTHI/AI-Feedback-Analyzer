import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import json
# import time # Not directly used for delays in app.py anymore
from io import StringIO, BytesIO
import zipfile

# --- Import Custom Utility Modules ---
from utils.clean import ingest_and_clean_data
# Import the new get_chat_response function
from utils.gemini_api import get_sentiment, extract_topics, generate_overall_summary, get_chat_response
from utils.visualize import plot_sentiment_distribution, generate_word_cloud
from utils.styling import apply_base_styles, set_theme_js

# --- Configuration & Setup ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("🚨 GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

st.set_page_config(
    page_title="AI Customer Feedback Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme Toggle Functionality ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

apply_base_styles(st.session_state.theme == 'dark')

def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'
    set_theme_js(st.session_state.theme == 'dark')
    st.rerun()

# --- Initialize Session State for Data & Analysis Results ---
if 'cleaned_feedback' not in st.session_state:
    st.session_state.cleaned_feedback = []
if 'raw_df_preview' not in st.session_state:
    st.session_state.raw_df_preview = None
if 'file_type' not in st.session_state:
    st.session_state.file_type = None
if 'sentiments' not in st.session_state:
    st.session_state.sentiments = []
if 'topics_per_feedback' not in st.session_state:
    st.session_state.topics_per_feedback = []
if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'last_uploaded_file_name' not in st.session_state:
    st.session_state.last_uploaded_file_name = None
if 'analysis_completed' not in st.session_state:
    st.session_state.analysis_completed = False


# --- Header ---
st.markdown("""
<div style='background-color: var(--bg-secondary); padding: 1rem 2rem; border-radius: 8px; margin-bottom: 2rem;'>
  <h1 style='color: var(--header-color); margin-top:0;'>🧠 AI Customer Feedback Analyzer</h1>
  <p style='color: var(--text-color); margin-bottom:0;'>Upload your customer reviews and let AI do the analysis for you.</p>
</div>
""", unsafe_allow_html=True)


# --- File Uploader and Theme Toggle ---
col1, col2 = st.columns([0.8, 0.2])

with col1:
    uploaded_file = st.file_uploader(
        "📤 Upload a CSV, JSON or TXT file",
        type=["csv", "json", "txt"],
        help="CSV (with 'feedback_text' column), JSON (list of objects with 'feedback' field), or plain TXT (one feedback per line)."
    )

with col2:
    st.button(
        "💡 Toggle Theme",
        on_click=toggle_theme,
        help=f"Switch to {'Light' if st.session_state.theme == 'dark' else 'Dark'} Mode"
    )

# --- Main Processing Logic ---
if uploaded_file is not None:
    # Check if a new file is uploaded or if existing data needs reprocessing
    if st.session_state.last_uploaded_file_name != uploaded_file.name:
        st.session_state.last_uploaded_file_name = uploaded_file.name
        
        # Reset analysis flags and data when a new file is uploaded
        st.session_state.cleaned_feedback = []
        st.session_state.sentiments = []
        st.session_state.topics_per_feedback = []
        st.session_state.ai_summary = ""
        st.session_state.chat_history = []
        st.session_state.analysis_completed = False
        st.session_state.raw_df_preview = None
        st.session_state.file_type = uploaded_file.name.split('.')[-1].lower()

        with st.spinner("Ingesting and cleaning data..."):
            try:
                file_content = uploaded_file.getvalue()
                
                # --- Preview raw data ---
                if st.session_state.file_type == 'csv':
                    st.session_state.raw_df_preview = pd.read_csv(StringIO(file_content.decode("utf-8")), nrows=5)
                elif st.session_state.file_type == 'json':
                    try:
                        full_json_data = json.loads(file_content.decode("utf-8"))
                        if isinstance(full_json_data, list) and all(isinstance(item, dict) for item in full_json_data):
                            st.session_state.raw_df_preview = pd.DataFrame(full_json_data).head(5)
                        else:
                            st.session_state.raw_df_preview = pd.DataFrame({"Error": ["Invalid JSON structure for preview (expected list of objects)"]})
                    except json.JSONDecodeError:
                        st.session_state.raw_df_preview = pd.DataFrame({"Error": ["Invalid JSON format for preview"]})

                lemmatize_option = st.checkbox("Apply Lemmatization (more advanced text normalization)", value=False)
                st.session_state.cleaned_feedback = ingest_and_clean_data(StringIO(file_content.decode("utf-8")), st.session_state.file_type, apply_lemmatization=lemmatize_option)
                st.success("✅ File uploaded and preprocessing initiated!")
                
            except ValueError as ve:
                st.error(f"Data Processing Error: {ve}. Please check file format and content.")
                st.session_state.cleaned_feedback = []
                st.session_state.last_uploaded_file_name = None
            except Exception as e:
                st.error(f"An unexpected error occurred during file ingestion: {e}")
                st.session_state.cleaned_feedback = []
                st.session_state.last_uploaded_file_name = None
        
        st.rerun()

    # --- File Summary & Preprocessing Stats ---
    if st.session_state.cleaned_feedback:
        st.markdown("### File Summary & Preprocessing Stats")
        col_sum1, col_sum2 = st.columns(2)
        with col_sum1:
            st.success(f"✅ Total Feedbacks Loaded: **{len(st.session_state.cleaned_feedback)}**")
        with col_sum2:
            st.info("💡 Cleaning Applied: Lowercase, punctuation/HTML/URLs removed, optional lemmatization.")

        if st.session_state.raw_df_preview is not None and not st.session_state.raw_df_preview.empty:
            st.markdown("##### Raw Data Preview (First 5 rows)")
            st.dataframe(st.session_state.raw_df_preview)
        elif st.session_state.file_type == 'txt':
             st.markdown(f"##### Plain Text File: {len(st.session_state.cleaned_feedback)} lines detected.")
        
        st.markdown("---")

        # --- Run AI Analysis Button ---
        if not st.session_state.analysis_completed:
            if st.button("🎯 Run AI Analysis", key="run_ai_analysis_button"):
                with st.spinner("Starting AI analysis, this may take a moment..."):
                    progress_text = "Analyzing feedback with AI..."
                    ai_progress_bar = st.progress(0, text=progress_text)
                    
                    total_feedback = len(st.session_state.cleaned_feedback)
                    
                    temp_sentiments = []
                    temp_topics_for_df = []

                    for i, feedback in enumerate(st.session_state.cleaned_feedback):
                        # Sentiment Analysis (uses built-in retry)
                        sentiment = get_sentiment(feedback)
                        temp_sentiments.append(sentiment)

                        # Topic Extraction (uses built-in retry)
                        topics = extract_topics(feedback)
                        temp_topics_for_df.append(", ".join(topics) if topics else "")

                        progress_percentage = (i + 1) / total_feedback
                        ai_progress_bar.progress(progress_percentage, text=f"{progress_text} ({i+1}/{total_feedback})")
                        
                    st.session_state.sentiments = temp_sentiments
                    st.session_state.topics_per_feedback = temp_topics_for_df
                    ai_progress_bar.empty()
                    
                    # Generate Overall Summary only once per analysis run (uses built-in retry)
                    with st.spinner("Generating overall AI summary..."):
                        st.session_state.ai_summary = generate_overall_summary(st.session_state.cleaned_feedback)
                    
                    st.session_state.analysis_completed = True
                    st.success("AI analysis complete!")
                    st.rerun()
            else:
                st.info("Click '🎯 Run AI Analysis' to process feedback with Gemini.")
        else:
            st.success("✅ AI Analysis already completed for this file.")


# --- Display Results & Visualizations (if analysis results exist) ---
if st.session_state.analysis_completed and st.session_state.sentiments:
    st.subheader("📊 Visual Results")

    st.markdown("#### Sentiment Distribution Chart")
    plot_sentiment_distribution(st.session_state.sentiments)

    st.markdown("#### Themes Word Cloud")
    all_individual_topics = []
    for topic_string in st.session_state.topics_per_feedback:
        all_individual_topics.extend([t.strip() for t in topic_string.split(',') if t.strip()])
    generate_word_cloud(all_individual_topics)
    
    # --- AI Summary Output ---
    st.markdown("#### 📌 AI Summary Output")
    
    if st.session_state.ai_summary:
        st.markdown(f"<div style='background-color: var(--bg-secondary); padding: 1rem; border-radius: 8px;'>", unsafe_allow_html=True)
        st.markdown(st.session_state.ai_summary)
        st.markdown(f"</div>", unsafe_allow_html=True)

    else:
        st.warning("AI summary not available. Please run the analysis.")

    st.markdown("---")
    
    # --- Chat with Feedback Feature ---
    st.subheader("🤖 Chat with Your Feedback Data")
    st.markdown("Ask questions about the feedback like: 'What are the main complaints about shipping?' or 'What do customers love most?'")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the feedback..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_context_limit = 50 # Limit context to first 50 entries
                chat_context = "\n".join(st.session_state.cleaned_feedback[:chat_context_limit]) 

                chat_prompt = (
                    f"You are an AI assistant analyzing customer feedback. "
                    f"Based on the following feedback snippets and the overall AI summary:\n\n"
                    f"Feedback Snippets:\n{chat_context}\n\n"
                    f"Overall AI Summary:\n{st.session_state.ai_summary}\n\n"
                    f"User's Question: {prompt}\n\n"
                    f"Please provide a concise and helpful answer."
                )
                
                try:
                    # Use the new get_chat_response function
                    full_response = get_chat_response(chat_prompt)
                except Exception as e:
                    full_response = f"I apologize, but I encountered an error trying to answer that: {e}"
            st.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

else:
    if not st.session_state.cleaned_feedback and uploaded_file is None:
        st.info("Please upload a feedback file to begin the analysis.")
    elif st.session_state.cleaned_feedback and not st.session_state.analysis_completed:
        st.info("File loaded. Click '🎯 Run AI Analysis' to process feedback with Gemini.")

st.markdown("---")

# --- Action Bar (Bottom Section - ENHANCED EXPORT) ---
if st.session_state.analysis_completed:
    col_actions1, col_actions2 = st.columns([1, 1])
    
    with col_actions1:
        # Create DataFrame for analyzed data
        analyzed_df = pd.DataFrame({
            "Feedback_Text_Cleaned": st.session_state.cleaned_feedback,
            "Sentiment": st.session_state.sentiments,
            "Topics": st.session_state.topics_per_feedback
        })

        # Prepare files for ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # 1. Add AI Summary
            ai_summary_filename = "ai_summary.md"
            summary_content = (
                f"AI Customer Feedback Analysis Report Summary\n"
                f"---------------------------------------------\n\n"
                f"Total Feedbacks Analyzed: {len(st.session_state.cleaned_feedback)}\n\n"
                f"{st.session_state.ai_summary}\n\n"
                f"---------------------------------------------\n"
                f"Generated by AI Customer Feedback Analyzer"
            )
            zip_file.writestr(ai_summary_filename, summary_content)

            # 2. Add Analyzed Data CSV
            analyzed_data_filename = "analyzed_feedback_data.csv"
            csv_string = analyzed_df.to_csv(index=False, encoding='utf-8')
            zip_file.writestr(analyzed_data_filename, csv_string)
            
        zip_buffer.seek(0)

        st.download_button(
            label="📁 Export Report (ZIP)",
            data=zip_buffer,
            file_name="ai_feedback_report.zip",
            mime="application/zip",
            help="Download a ZIP file containing the AI summary (markdown) and detailed analyzed data (CSV)."
        )
    
    with col_actions2:
        if st.button("🔄 Reset Application", help="Clear all data and restart the application."):
            st.session_state.clear()
            st.experimental_rerun()

st.markdown("---")
st.markdown("Powered by Google Gemini & Streamlit")