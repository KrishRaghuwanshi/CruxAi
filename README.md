DocAnalyzer: Summarize & Transform

This is a Streamlit application that uses LangChain and Google's Gemini Pro to summarize large documents and extract additional insights.

Features

Summarize Anything: Provides a cohesive summary for large text from PDFs, .txt files, or blog URLs.

Map-Reduce: Uses LangChain's map_reduce chain to process documents of any length.

Bonus Content:

Key Takeaways: Extracts the most important points.

Keywords & Topics: Identifies core themes.

Social Media: Repurposes content for LinkedIn and Twitter.

Setup & Running

Clone/Download:
Get the code into a local directory named SummarizerApp.

Create a Virtual Environment (Recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:

pip install -r requirements.txt


Set Your API Key:
This app requires a Google API Key for the Gemini model.

Go to Google AI Studio to generate your key.

You can set this key as an environment variable (recommended for production):

export GOOGLE_API_KEY="YOUR_API_KEY_HERE"


...or, you can simply paste it into the sidebar of the Streamlit app when you run it.

Run the App:
From your terminal, inside the SummarizerApp directory, run:

streamlit run app.py


The application will open in your browser.