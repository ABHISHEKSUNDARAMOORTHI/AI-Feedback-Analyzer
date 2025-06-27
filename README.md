# 🧠 AI Customer Feedback Analyzer

## 📋 Overview

Welcome to the **AI Customer Feedback Analyzer**!  
This powerful Streamlit-based application helps businesses gain deeper insights into their customer feedback by leveraging **Google Gemini AI**.

Simply upload your feedback data (CSV, JSON, or TXT), and the app will:

- Analyze sentiment
- Extract key topics
- Generate an AI-powered summary
- Let you chat with your feedback for instant insights

---

## ✨ Features

- 📈 **Sentiment Analysis**  
  Automatically classifies each feedback entry as **Positive**, **Negative**, or **Neutral**.

- 💡 **Topic Extraction**  
  Identifies key themes and keywords from customer comments.

- 📝 **AI-Powered Summary**  
  Generates a comprehensive summary of the feedback, highlighting positive, negative, and actionable insights.

- 💬 **Interactive Chat**  
  Ask questions about your feedback data and get instant responses powered by Gemini.

- 📊 **Data Visualization**  
  View sentiment distribution charts and a word cloud of frequent topics.

- 📁 **Exportable Report**  
  Download a ZIP containing:
  - The summary in Markdown
  - Analyzed data in CSV

- ✨ **User-Friendly Interface**  
  Built with **Streamlit**, designed for ease of use and quick exploration.

- ⚙️ **Robust API Handling**  
  Implements exponential backoff and retry logic to gracefully handle API rate limits and quotas.

---

## 🛠 How It Works

### 🔄 1. Data Upload & Preprocessing

- Upload customer reviews via CSV, JSON, or TXT files.
- Data is cleaned by:
  - Lowercasing
  - Removing punctuation and URLs
  - (Optional) Lemmatization

### 🤖 2. AI-Powered Analysis

- For each entry, the app sends individual requests to Gemini to:
  - Detect sentiment
  - Extract keywords or topics
- Afterward, it generates a full summary across all feedback entries.

### 📊 3. Visualizations & Chat

- Visual dashboards: sentiment distribution and word cloud.
- Chat interface: ask natural language questions like:
  > "What are the top complaints?"  
  > "How do users feel about support?"  
  > "List all positive feedback themes."

### ⚠️ 4. Smart Error Handling

- Automatically retries failed requests (with exponential delay).
- Gracefully handles:
  - Quota exceeded (429 errors)
  - Model version mismatches
  - Timeout and SDK issues

---

## 📦 Setup & Installation

### ✅ Prerequisites

- Python 3.8+
- Google Gemini API Key (from [Google AI Studio](https://aistudio.google.com))

> ⚠️ Note: Free-tier API keys have strict limits (e.g., ~50 requests/day). For larger workloads, enable billing in your Google Cloud Project.

---

### 📥 Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/ai-customer-feedback-analyzer.git
cd ai-customer-feedback-analyzer
````

#### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Your API Key

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

Replace with your actual Gemini API key.

---

### ▶️ Run the Application

```bash
streamlit run app.py
```

Your browser should open at: `http://localhost:8501`

---

## 🗂️ Project Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Dependencies
├── .env                   # Gemini API Key
└── utils/
    ├── __init__.py
    ├── clean.py           # Data ingestion and cleaning
    ├── gemini_api.py      # Gemini API integration (sentiment, topics, summary, chat)
    ├── styling.py         # Streamlit theme and custom CSS
    └── visualize.py       # Charts and word cloud generation
```

---

## 🧩 Troubleshooting

### ❗ 429 Quota Exceeded or ResourceExhausted

* Your API quota has been exceeded.
* **Solution**: Wait 24 hours or enable billing for higher limits.

### ❗ AttributeError: `HarmCategory` has no attribute `HARASSMENT`

* Google SDK changed enum names.
* **Solution**: Use updated enums like `HARM_CATEGORY_HARASSMENT` in `gemini_api.py`.

### ❗ 404 Error: `models/gemini-pro` Not Found

* The specified model may not be available to your key.
* **Solution**: Use `gemini-1.5-flash` or other available models. Latest code auto-detects supported models.

### ❗ TypeError: `generate_content()` got unexpected keyword 'timeout'

* Your SDK version doesn’t support `timeout`.
* **Solution**: Remove `timeout=` from calls in `gemini_api.py` (already fixed in latest version).

---

## 🙌 Contributing

Pull requests are welcome!
To contribute:

1. Fork this repo
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Push and open a PR

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🌐 Author

Made with 💡 by **Abhishek Sundaramoorthi**

Let me know if you'd like a demo or if you're looking to integrate this into your customer success or support pipeline.
