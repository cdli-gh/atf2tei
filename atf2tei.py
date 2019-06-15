import re
from xml.sax.saxutils import escape

from pyoracc.atf.common.atffile import AtfFile
from pyoracc.model.line import Line
from pyoracc.model.oraccobject import OraccObject


def convert(infile):
    """
    Create a TEI representation of a file-like object containing ATF.
    """
    atf = AtfFile(infile.read(), 'cdli', False)
    print("Parsed {} -- {}".format(atf.text.code, atf.text.description))
    result = '''
<TEI xmlns="http://www.tei-c.org/ns/1.0">

<teiHeader>
<fileDesc>
  <titleStmt>
    <title>{description}</title>
  </titleStmt>
  <publicationStmt>
    <p>Converted from ATF by atf2tei.</p>
  </publicationStmt>
  <sourceDesc>
    <idno type="CDLI">{code}</idno>
  </sourceDesc>
</fileDesc>
</teiHeader>
'''.format(description=atf.text.description, code=atf.text.code)
    result += '''
<text>
<body>
'''
    for item in atf.text.children:
        if isinstance(item, OraccObject):
            result += f'  <div type="{item.objecttype}">\n'
        else:
            result += '  <div>\n' \
                     f'<!-- {type(item).__name__}: {item} -->\n'
        for section in item.children:
            if isinstance(section, OraccObject):
                result += f'    <div type="{section.objecttype}">\n'
            else:
                result += '    <div>\n' \
                         f'<!-- {type(section).__name__}: {section} -->\n'
            offset = 1
            for index, line in enumerate(section.children):
                if isinstance(line, Line):
                    text = normalize_transliteration(line.words)
                    result += f'      <l n="{index + offset}">{text}</l>\n'
                else:
                    result += f'      <!-- {type(line).__name__}: {line} -->\n'
            offset += len(section.children)
            result += '    </div>\n'
        result += '  </div>\n'
    result += '''
</body>
</text>
</TEI>'''
    return result


def normalize_transliteration(words):
    '''Convert a sequence of words from atf to standard formatting.'''
    # See http://oracc.org/doc/help/editinginatf/primer/inlinetutorial/
    result = []
    for word in words:
        '''Convert digraphs to corresponding unicode characters.'''
        word = re.sub(r'sz', 'š', word)     # \u0161
        word = re.sub(r'SZ', 'Š', word)     # \u0160
        word = re.sub(r's,', 'ṣ', word)     # \u1E63
        word = re.sub(r'S.', 'Ṣ', word)     # \u1E62
        word = re.sub(r't,', 'ṭ', word)     # \u1E6D
        word = re.sub(r'T,', 'Ṭ', word)     # \u1E6C
        word = re.sub(r's\'', 'ś', word)    # \u015B
        word = re.sub(r'S\'', 'Ś', word)    # \u015A
        word = re.sub(r'h,', 'ḫ', word)     # \u1E2B
        word = re.sub(r'H,', 'Ḫ', word)     # \u1E2A
        word = re.sub(r'j', 'ŋ', word)      # \u014B
        word = re.sub(r'J', 'Ŋ', word)      # \u014A
        '''XML-escape the result.'''
        word = escape(word)
        '''Convert markup to tei elements.'''
        word = re.sub(r'{([^{}]+)}', r'<hi rend="superscript">\1</hi>', word)
        word = re.sub(r'_(\w+)', r'<emph rend="small-caps">\1', word)
        word = re.sub(r'(\w+)_', r'\1</emph>', word)
        result.append(word)
    return ' '.join(result)


if __name__ == '__main__':
    import io
    import sys
    for filename in sys.argv[1:]:
        with io.open(filename, encoding='utf-8') as f:
            xml = convert(f)
            print(xml)
