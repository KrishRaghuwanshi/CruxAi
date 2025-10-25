import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import StringIO, BytesIO
import re
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

def clean_text(text: str) -> str:
    """Cleans text by removing excessive whitespace and special characters."""
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    return text

def load_pdf(file_bytes: BytesIO) -> str:
    """
    Reads a PDF file-like object and extracts text.
    'file_bytes' should be a BytesIO object.
    """
    reader = PdfReader(file_bytes)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return clean_text(full_text)

def load_txt(file_io: StringIO) -> str:
    """
    Reads a text file-like object.
    'file_io' should be a StringIO object.
    """
    return clean_text(file_io.read())


def load_blog_url(url):
    try:
        # Set up session with retry logic
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # Number of retries
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[500, 502, 503, 504, 10054]  # Retry on these status codes and connection errors
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Custom user-agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Fetch the URL
        response = session.get(url, headers=headers, timeout=10)  # 10-second timeout
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse with BeautifulSoup using lxml
        soup = BeautifulSoup(response.content, 'lxml')
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")