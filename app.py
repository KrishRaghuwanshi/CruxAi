import streamlit as st
import os
from io import BytesIO, StringIO
import src.data_loader as loader
import src.summarizer as processor
from dotenv import load_dotenv


# --- Page Configuration ---
st.set_page_config(
    page_title="DocAnalyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Load API Key from .env file ---
# This MUST be one of the first things to run
load_dotenv()

# --- 2. Add API Key Check ---
# We check this *after* loading and *before* any UI
if not os.getenv("GOOGLE_API_KEY"):
    st.error("🚨 GOOGLE_API_KEY not found in .env file!")
    st.info("Please create a .env file in the app root directory and add your API key like this: GOOGLE_API_KEY='your_key_here'")
    st.stop() # Stop the app if no key

# --- Aesthetic Styling ---
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 2px solid #F0F0F0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #357ABD;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab"] {
        background-color: #F0F0F0;
        border-radius: 8px 8px 0 0;
        margin-right: 5px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF;
        font-weight: 600;
    }
    
    /* Expander styling */
    .stExpander {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'summary' not in st.session_state:
    st.session_state['summary'] = None

# --- 3. OLD SIDEBAR CODE DELETED ---
# (The section that asked for the API key is now gone)

# --- 4. New Sidebar Content ---
st.sidebar.title("About")
st.sidebar.info("This app uses Google's Gemini Pro and LangChain to summarize and analyze documents.")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: left; color: #888888; font-size: 0.9em;'>Created by Krish Raghuwanshi</div>",
    unsafe_allow_html=True
)

# --- Main Application ---
st.title("📄 DocAnalyzer: Summarize & Transform")
st.markdown("Upload a document, paste a URL, or add text to get a comprehensive summary and generate bonus content.")

# --- Input Section ---
st.subheader("1. Provide Your Content")

tab1, tab2, tab3 = st.tabs(["📁 Upload File (.pdf, .txt)", "🔗 Blog URL", "✍️ Paste Text"])

full_text = None
source_name = None

with tab1:
    uploaded_file = st.file_uploader("Choose a .pdf or .txt file", type=["pdf", "txt"])
    if uploaded_file:
        source_name = uploaded_file.name
        with st.spinner(f"Reading {source_name}..."):
            try:
                if uploaded_file.type == "application/pdf":
                    # pypdf needs a file-like object
                    file_bytes = BytesIO(uploaded_file.getvalue())
                    full_text = loader.load_pdf(file_bytes)
                elif uploaded_file.type == "text/plain":
                    # Txt file needs to be decoded
                    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    full_text = loader.load_txt(stringio)
                st.success(f"Successfully loaded '{source_name}'")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                full_text = None

with tab2:
    url = st.text_input("Enter the URL of a blog post or article")
    if url:
        source_name = url
        with st.spinner(f"Scraping text from {url}..."):
            try:
                full_text = loader.load_blog_url(url)
                st.success("Successfully scraped text from URL.")
            except Exception as e:
                st.error(f"Error scraping URL: {e}")
                full_text = None

with tab3:
    pasted_text = st.text_area("Paste your text here", height=300)
    if pasted_text:
        source_name = "Pasted Text"
        full_text = pasted_text
        st.success("Text is ready for analysis.")

# --- Summarization Button & Logic ---
if st.button("Analyze Document", type="primary", disabled=(not full_text)):
    with st.spinner("Generating summary... This may take a moment for large documents."):
        try:
            st.session_state['summary'] = processor.summarize_document(full_text)
        except Exception as e:
            st.error(f"Error during summarization: {e}")
            st.session_state['summary'] = None

# --- Display Section (Summary & Bonus Features) ---
if st.session_state['summary']:
    st.divider()
    st.subheader("2. Analysis & Generation")

    col1, col2 = st.columns([6, 4])  # 60% width for summary, 40% for actions

    with col1:
        st.subheader("📄 Document Summary")
        st.markdown(st.session_state['summary'])

    with col2:
        st.subheader("✨ Generate More")
        
        options = [
            "Key Takeaways", 
            "Topic & Keyword Extractor", 
            "Content Repurposing (Social Media Posts)"
        ]
        
        selected_options = st.multiselect(
            "Select what you want to generate from the summary:",
            options
        )

        if st.button("Generate Selected Content"):
            if not selected_options:
                st.warning("Please select at least one option.")
            
            if "Key Takeaways" in selected_options:
                with st.spinner("Extracting key takeaways..."):
                    try:
                        takeaways = processor.get_takeaways(st.session_state['summary'])
                        with st.expander("🔑 Key Takeaways", expanded=True):
                            st.markdown(takeaways)
                    except Exception as e:
                        st.error(f"Error generating takeaways: {e}")

            if "Topic & Keyword Extractor" in selected_options:
                with st.spinner("Finding keywords..."):
                    try:
                        keywords = processor.get_keywords(st.session_state['summary'])
                        with st.expander("🏷️ Topics & Keywords", expanded=True):
                            st.markdown(keywords)
                    except Exception as e:
                        st.error(f"Error generating keywords: {e}")

            if "Content Repurposing (Social Media Posts)" in selected_options:
                with st.spinner("Creating social media posts..."):
                    try:
                        post = processor.generate_social_post(st.session_state['summary'])
                        with st.expander("📱 Social Media Posts", expanded=True):
                            st.markdown(post)
                    except Exception as e:
                        st.error(f"Error generating post: {e}")

# --- Footer ---
st.divider()
# (Footer credit is removed from here since it's now in the sidebar)

