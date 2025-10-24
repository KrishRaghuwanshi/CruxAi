import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import StringIO, BytesIO

def load_pdf(file_bytes: BytesIO) -> str:
    """
    Reads a PDF file-like object and extracts text.
    'file_bytes' should be a BytesIO object.
    """
    reader = PdfReader(file_bytes)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

def load_txt(file_io: StringIO) -> str:
    """
    Reads a text file-like object.
    'file_io' should be a StringIO object.
    """
    return file_io.read()

def load_blog_url(url: str) -> str:
    """
    Fetches and parses text from a blog URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'lxml')

        # Find all paragraphs, which usually contain the main content
        paragraphs = soup.find_all('p')
        
        full_text = ""
        for p in paragraphs:
            full_text += p.get_text() + "\n\n"
            
        if not full_text:
            # Fallback for pages that don't use <p>
            full_text = soup.get_text()

        return full_text

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {e}")
