from . import views
from .util import get_entry, save_entry, list_entries
from markdown2 import markdown

def html_code(title):
    content = get_entry(title)
    if content:
        return markdown(content)
    else:
        return None
    

