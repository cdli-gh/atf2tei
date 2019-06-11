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
            for line in section.children:
                if isinstance(line, Line):
                    result += f'      <l>{escape(" ".join(line.words))}</l>\n'
                else:
                    result += f'      <!-- {type(line).__name__}: {line} -->\n'
            result += '    </div>\n'
        result += '  </div>\n'
    result += '''
</body>
</text>
</TEI>'''
    return result


if __name__ == '__main__':
    import io
    import sys
    for filename in sys.argv[1:]:
        with io.open(filename, encoding='utf-8') as f:
            xml = convert(f)
            print(xml)
