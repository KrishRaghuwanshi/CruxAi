import os
import streamlit as st  # Import streamlit for st.info/st.error
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- NOTE: "load_summarize_chain" IS GONE. This is correct. ---

# This is a helper function to initialize the LLM
def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the ChatGoogleGenerativeAI model.
    Reads the API key from the environment.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=api_key,
        temperature=0.3,
    )

# --- 1. Main Summarization Function (NEW LCEL MAP-REDUCE) ---

def summarize_document(full_text: str) -> str:
    """
    Summarizes a large document using the Map-Reduce strategy,
    built manually with LangChain Expression Language (LCEL).
    """
    llm = _get_llm()
    
    # 1. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8192,
        chunk_overlap=200
    )
    docs = text_splitter.create_documents([full_text])

    # 2. MAP step: Define the chain for summarizing one chunk
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

    # 3. Run the MAP step in parallel on all chunks
    try:
        st.info(f"Summarizing {len(docs)} chunks (Map step)...")
        list_of_summaries = map_chain.batch(docs, {"max_concurrency": 5})
    except Exception as e:
        st.error(f"Error during 'Map' step: {e}")
        return "Summary generation failed during the map step."

    # 4. COMBINE step: Join all the summaries into one string
    combined_summaries = "\n\n".join(list_of_summaries)

    # 5. REDUCE step: Define the chain for the final summary
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

    # 6. Run the REDUCE step
    try:
        st.info("Creating final summary (Reduce step)...")
        final_summary = reduce_chain.invoke(combined_summaries)
        return final_summary
    except Exception as e:
        st.error(f"Error during 'Reduce' step: {e}")
        return "Summary generation failed during the reduce step."

# --- 2. Bonus Feature Functions (These are working and unchanged) ---

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

