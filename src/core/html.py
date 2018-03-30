from bs4 import BeautifulSoup
from flask_misaka import markdown


def html2text(html: str) -> str:
    """ Extract plain text from
    markdown generated html description."""
    b = BeautifulSoup(html, 'lxml')
    b.a.decompose() if b.a else ''
    b.img.decompose() if b.img else ''
    b.table.decompose() if b.table else ''
    b.code.decompose() if b.code else ''
    text = b.get_text()
    return text.replace('\n', ' ').replace('  ', ' ').strip()


def markdown2html(text: str) -> str:
    opts = {
        'autolink': True,
        'underline': True,
        'space_headers': False,
        'no_intra_emphasis': True,
        'tables': True,
        'wrap': True,
        'escape': False,
        'skip_html': False,
        'smartypants': True,

    }
    m = markdown(text, options=opts)
    return m
