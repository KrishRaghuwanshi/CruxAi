import streamlit as st
import os
from io import BytesIO, StringIO
import src.data_loader as loader
import src.summarizer as processor
from dotenv import load_dotenv


st.set_page_config(
    page_title="CruxAi",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

api_key = os.getenv("GOOGLE_API_KEY")


if not os.getenv("GOOGLE_API_KEY"):
    st.error("🚨 GOOGLE_API_KEY not found")
    st.info("Please add your API key like this: GOOGLE_API_KEY='your_key_here'")
    st.stop()


st.markdown("""
<style>
    /* Import Poppins font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    /* App-wide dark mode styling */
    .stApp {
        background-color: #1E1E1E;
        color: #E0E0E0;
        font-family: 'Poppins', sans-serif;
    }

    /* Header styling */
    .header-container {
        text-align: center;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
    }
    .title {
        font-size: 4.5em;
        font-weight: 700;
        color: #4A90E2;
        animation: pulseText 2s infinite ease-in-out;
        display: inline-block;
    }
    .creator {
        font-size: 0.7em;
        color: #888888;
        display: block;
        margin-top: -10px;
    }
    @keyframes pulseText {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    /* Creative Separator */
    .separator {
        width: 50%;
        height: 2px;
        background: linear-gradient(to right, transparent, #4A90E2, transparent);
        margin: 1rem auto;
        position: relative;
    }
    .separator::before {
        content: '';
        position: absolute;
        top: -5px;
        left: 50%;
        transform: translateX(-50%);
        width: 10px;
        height: 10px;
        background-color: #4A90E2;
        border-radius: 50%;
        animation: pulseDot 1.5s infinite ease-in-out;
    }
    @keyframes pulseDot {
        0% { transform: translateX(-50%) scale(1); opacity: 0.5; }
        50% { transform: translateX(-50%) scale(1.2); opacity: 1; }
        100% { transform: translateX(-50%) scale(1); opacity: 0.5; }
    }

    /* Input section */
    .input-section {
        background-color: #2E2E2E;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: fadeIn 1s ease-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab"] {
        background-color: #3E3E3E;
        color: #4A90E2;
        border: none;
        padding: 10px 20px;
        border-radius: 10px 10px 0 0;
        margin-right: 5px;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #4A90E2;
        color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #4A90E2;
        color: #FFFFFF;
        box-shadow: 0 2px 6px rgba(74, 144, 226, 0.2);
    }

    /* Button styling */
    .stButton > button {
        background-color: #4A90E2;
        color: #FFFFFF;
        border: none;
        padding: 12px 25px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
    }
    .stButton > button:hover {
        background-color: #357ABD;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
    }
    .stButton > button:disabled {
        background-color: #666666;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }

    /* Result section */
    .result-section {
        background-color: #2E2E2E;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        animation: slideUp 1s ease-out;
    }
    @keyframes slideUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Expander styling */
    .stExpander {
        background-color: #3E3E3E;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stExpander[aria-expanded="true"] {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        background-color: #4A90E2;
        color: #FFFFFF;
    }

    /* Messages */
    .stError, .stWarning, .stInfo {
        background-color: #2E2E2E;
        border-left: 4px solid #4A90E2;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.5s ease-out;
    }

    /* Spinner animation */
    .stSpinner {
        text-align: center;
        color: #4A90E2;
        font-size: 1.2em;
    }
    .stSpinner::after {
        content: "⏳";
        animation: spin 1s infinite linear;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Animated Header for Analysis & Generation */
    .animated-header {
        animation: fadeInHeader 1s ease-out;
    }
    @keyframes fadeInHeader {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'summary' not in st.session_state:
    st.session_state['summary'] = None
if 'processing' not in st.session_state:
    st.session_state['processing'] = False
if 'generating' not in st.session_state:
    st.session_state['generating'] = False

# --- Main Application ---
st.markdown('<div class="header-container"><div class="title">CruxAi</div><div class="creator">Created by Krish Raghuwanshi</div></div>', unsafe_allow_html=True)
st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# --- Input Section ---
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.header("Provide Your Content")

tab1, tab2, tab3 = st.tabs(["📁 Upload File", "🔗 Blog URL", "✍️ Paste Text"])

full_text = None
source_name = None

with tab1:
    uploaded_file = st.file_uploader("Upload a .pdf or .txt file", type=["pdf", "txt"])
    if uploaded_file:
        source_name = uploaded_file.name
        with st.spinner("Loading..."):
            try:
                if uploaded_file.type == "application/pdf":
                    file_bytes = BytesIO(uploaded_file.getvalue())
                    full_text = loader.load_pdf(file_bytes)
                elif uploaded_file.type == "text/plain":
                    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    full_text = loader.load_txt(stringio)
                st.success("Content loaded successfully! 📥")
            except Exception as e:
                st.error(f"Error loading content: {e}")
                full_text = None

with tab2:
    url = st.text_input("Enter the URL of a blog post")
    if url:
        source_name = url
        with st.spinner("Loading..."):
            try:
                full_text = loader.load_blog_url(url)
                st.success("Content loaded successfully! 🌐")
            except Exception as e:
                st.error(f"Error loading content: {e}")
                full_text = None

with tab3:
    pasted_text = st.text_area("Paste your text here", height=300)
    if pasted_text:
        source_name = "Pasted Text"
        with st.spinner("Loading..."):
            try:
                full_text = pasted_text
                st.success("Content loaded successfully! ✍️")
            except Exception as e:
                st.error(f"Error loading content: {e}")
                full_text = None

# --- Summarization Button & Logic ---
@st.cache_data(show_spinner=False)
def cached_summarize_document(full_text: str) -> str:
    try:
        result = processor.summarize_document(full_text)
        if not result or not result.strip():
            st.warning("Summary generation failed. Please try different content.")
            return "No summary generated."
        return result
    except Exception as e:
        st.error(f"Summary generation failed: {e}")
        return f"Summary error occurred."

if st.button("Summarize 📊", type="primary", disabled=(not full_text or st.session_state['processing'])):
    if not full_text.strip() or len(full_text.strip()) < 50:
        st.error("Content is too short or invalid. Please provide at least 50 characters. 🚫")
    else:
        st.session_state['processing'] = True
        with st.spinner("Generating Content..."):
            try:
                st.session_state['summary'] = cached_summarize_document(full_text)
                if not st.session_state['summary'] or not st.session_state['summary'].strip():
                    st.warning("Summary generation resulted in no valid content.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.session_state['summary'] = None
            finally:
                st.session_state['processing'] = False

# --- Display Section (Summary & Bonus Features) ---
if st.session_state['summary'] is not None:
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="animated-header">Analysis & Generation 🎯</h2>', unsafe_allow_html=True)

    if st.session_state['summary'] and st.session_state['summary'].strip():
        st.markdown(f"### Document Summary\n{st.session_state['summary']}")
    else:
        st.error("Summary generation failed. Please try different content or check API limits. 🚨")

    options = [
        "🔑 Key Takeaways",
        "🏷️ Topic & Keyword Extractor",
        "📈 LinkedIn Post",
        "🐦 Twitter Post"
    ]

    selected_options = st.multiselect(
        "Select what to generate from the summary:",
        options
    )

    if st.button("Generate Extra Content 🌟", disabled=not (st.session_state['summary'] and st.session_state['summary'].strip()) or st.session_state['generating']):
        if not selected_options:
            st.warning("Please select at least one option. ⚠️")
        else:
            st.session_state['generating'] = True
            with st.spinner("Generating Content..."):
                try:
                    for option in selected_options:
                        if option == "🔑 Key Takeaways":
                            takeaways = processor.get_takeaways(st.session_state['summary'])
                            with st.expander("Key Takeaways", expanded=True):
                                if takeaways and takeaways.strip():
                                    st.markdown(takeaways)
                                else:
                                    st.warning("Takeaways generation failed. ⚠️")
                        elif option == "🏷️ Topic & Keyword Extractor":
                            keywords = processor.get_keywords(st.session_state['summary'])
                            with st.expander("Topics & Keywords", expanded=True):
                                if keywords and keywords.strip():
                                    st.markdown(keywords)
                                else:
                                    st.warning("Keywords generation failed. ⚠️")
                        elif option == "📈 LinkedIn Post":
                            post = processor.generate_social_post(st.session_state['summary'])
                            with st.expander("LinkedIn Post", expanded=True):
                                if post and post.strip():
                                    st.markdown(post)
                                else:
                                    st.warning("Post generation failed. ⚠️")
                        elif option == "🐦 Twitter Post":
                            twitter_post = processor.generate_twitter_post(st.session_state['summary'])
                            with st.expander("Twitter Post", expanded=True):
                                if twitter_post and twitter_post.strip():
                                    st.markdown(twitter_post)
                                else:
                                    st.warning("Twitter post generation failed. ⚠️")
                except Exception as e:
                    st.error(f"Generation error: {e}")
                finally:
                    st.session_state['generating'] = False

    st.markdown('</div>', unsafe_allow_html=True)