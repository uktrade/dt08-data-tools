import re
import zipfile

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def striptradegov(data):
    p = re.compile(r'tradegov(\w)*')
    return p.sub('', data)


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)