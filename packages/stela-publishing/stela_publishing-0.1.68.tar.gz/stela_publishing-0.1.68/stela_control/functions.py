from bs4 import BeautifulSoup

def caption_optimizer(html):
    soup = BeautifulSoup(html, 'html.parser')
    clear_text = soup.get_text(separator='\n\n')
    return clear_text