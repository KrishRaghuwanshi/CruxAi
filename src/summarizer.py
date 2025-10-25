import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# This is a helper function to initialize the LLM
def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the ChatGoogleGenerativeAI model.
    Reads the API key from the environment.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment.")

    # This prevents the model from returning a blank response due to safety filters
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key,
        temperature=0.3,
        max_retries=5,
        safety_settings=safety_settings
    )

# --- 1. Main Summarization Function (LCEL MAP-REDUCE) ---
def summarize_document(full_text: str) -> str:
    """
    Summarizes a large document using the Map-Reduce strategy,
    built manually with LangChain Expression Language (LCEL).
    """
    llm = _get_llm()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8192,
        chunk_overlap=200
    )
    docs = text_splitter.create_documents([full_text])

    map_prompt_template = """
    You are a helpful assistant who summarizes text.
    Summarize the following text chunk concisely and clearly:
    {text}
    CONCISE SUMMARY:
    """
    map_prompt = PromptTemplate.from_template(map_prompt_template)
    
    map_chain = (
        {"text": lambda doc: doc.page_content} 
        | map_prompt 
        | llm 
        | StrOutputParser()
    )

    try:
        st.info(f"Summarizing {len(docs)} chunks (Map step)...")
        list_of_summaries = map_chain.batch(docs, {"max_concurrency": 2})
        if not list_of_summaries:
            st.warning("No summaries generated during map step.")
            return "No summary generated due to empty results."
    except Exception as e:
        st.error(f"Error during 'Map' step: {e}")
        if "429" in str(e):
            st.error("Hit Google API rate limit (2 calls/min). Please wait a minute and try again.")
        return f"Summary generation failed during the map step: {str(e)}"

    combined_summaries = "\n\n".join(list_of_summaries)

    reduce_prompt_template = """
    You are an expert at synthesizing information.
    Take the following collection of summaries and create one, final, cohesive summary
    that covers all the main points.
    COLLECTION OF SUMMARIES:
    {summaries}
    FINAL COHESIVE SUMMARY:
    """
    reduce_prompt = PromptTemplate.from_template(reduce_prompt_template)
    
    reduce_chain = (
        {"summaries": lambda x: x}
        | reduce_prompt 
        | llm 
        | StrOutputParser()
    )

    try:
        st.info("Creating final summary (Reduce step)...")
        final_summary = reduce_chain.invoke(combined_summaries)
        if not final_summary or not final_summary.strip():
            st.warning("Empty summary generated during reduce step.")
            return "No valid summary generated."
        return final_summary
    except Exception as e:
        st.error(f"Error during 'Reduce' step: {e}")
        if "429" in str(e):
            st.error("Hit Google API rate limit (2 calls/min). Please wait a minute and try again.")
        return f"Summary generation failed during the reduce step: {str(e)}"

# --- 2. Bonus Feature Functions ---
def get_takeaways(summary: str) -> str:
    llm = _get_llm()
    prompt_template = """
    You are an expert analyst. From the following text, extract the 5 most important key takeaways.
    Present them as a concise, bulleted list. TEXT: "{text}" KEY TAKEAWAYS:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": summary})

def get_keywords(summary: str) -> str:
    llm = _get_llm()
    prompt_template = """
    You are an expert in text analysis. From the following text, extract:
    1. The 5 main topics
    2. The 10 most relevant keywords
    Present them as two separate lists. TEXT: "{text}" TOPICS & KEYWORDS:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": summary})

def generate_social_post(summary: str) -> str:
    llm = _get_llm()
    prompt_template = """
    You are a professional social media manager. Based on the following summary, write an engaging 
    and professional LinkedIn post. Include 3-5 relevant hashtags.
    SUMMARY: "{text}" LINKEDIN POST:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": summary})

def generate_twitter_post(summary: str) -> str:
    """
    Generates a concise Twitter post (≤280 characters) based on the summary, including 2-3 hashtags.
    """
    llm = _get_llm()
    prompt_template = """
    You are a professional social media manager. Based on the following summary, write a concise and engaging Twitter post . Include 2-3 relevant hashtags.
    SUMMARY: "{text}" TWITTER POST:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    twitter_post = chain.invoke({"text": summary})
    # Ensure the post is within 280 characters
    if len(twitter_post) > 280:
        twitter_post = twitter_post[:277] + "..."
    return twitter_post