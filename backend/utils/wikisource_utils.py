import requests
from bs4 import BeautifulSoup

def extract_direct_file_url(wikisource_file_page_url):
    """
    Given a Wikisource file page URL, return the direct file URL (PDF/DjVu).
    """
    resp = requests.get(wikisource_file_page_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Look for a link ending in .pdf or .djvu
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith((".pdf", ".djvu")) and "upload.wikimedia.org" in href:
            if href.startswith("//"):
                return "https:" + href
            elif href.startswith("http"):
                return href
            else:
                return "https://en.wikisource.org" + href
    return None 