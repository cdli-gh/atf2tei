from pyoracc.atf.common.atffile import AtfFile
from pyoracc.model.line import Line


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
        result += '  <div type="{}">\n'.format(item.objecttype)
        for section in item.children:
            result += '    <div type="{}">\n'.format(section.objecttype)
            for line in section.children:
                if isinstance(line, Line):
                    result += '      <l>{}</l>\n'.format(' '.join(line.words))
                else:
                    result += '      <!-- {}: {} -->\n'.format(
                        type(line).__name__, line)
            result += '    </div>\n'
        result += '  </div>\n'
    result += '''
</body>
</text>
</TEI>
'''
    return result


if __name__ == '__main__':
    import sys
    for filename in sys.argv[1:]:
        with open(filename) as f:
            xml = convert(f)
            print(xml)
