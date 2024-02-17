__all__ = [
    'is_url',
    'is_html',
    'url_to_html',
    'html_to_text',
]

def is_url(arg):
    if isinstance(arg, bytes):
        arg = arg.decode()
    import validators
    return bool(validators.url(arg))

def is_html(arg):
    if isinstance(arg, bytes):
        arg = arg.decode()
    for tag in ('<html', '<doctype', '<meta'):
        if tag in arg.lower():
            return True
    return False

def url_to_html(url):
    import requests
    return requests.get(url).content.decode()

def html_to_text(html):
    import bs4
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup.text

to_text = html_to_text
