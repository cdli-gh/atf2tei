#!/usr/bin/env python3

'''Convert a TEI XML document in the ATF.

Used by the Cuneiform Digital Library Initiative.
'''

import io
import sys
import xml.etree.ElementTree as ET

import tei


def convert(fp):
    'Read TEI XML from the given file-like object and return ATF.'
    xml = ET.fromstring(fp.read())
    ns = {
        'tei': tei.namespace,
        'xml': 'http://www.w3.org/XML/1998/namespace',
    }
    print(xml.find('tei:text', ns))

    # Collection of lines for output.
    atf = []

    # Fetch data for the header.
    title = xml.find('./tei:teiHeader//tei:title', ns).text
    code = xml.find('./tei:teiHeader//tei:idno', ns).text
    edition = xml.find('./tei:text//tei:div[@type="edition"]', ns)
    language = edition.get(f'{{{ns["xml"]}}}lang')

    # Construct the header.
    atf.append(f'&{code} = {title}')
    atf.append(f'#atf: lang {language}')

    # Loop over parts adding labels.
    for obj in edition.findall('tei:div', ns):
        print(obj.tag)
        atf.append('@' + obj.get('n'))
        for surface in obj.findall('tei:div', ns):
            print(surface.tag)
            atf.append('@' + surface.get('n'))
            for line in surface.findall('tei:l', ns):
                print(line.tag)
                atf.append(f'{line.get("n")}. {line.text}')

    # Return the ATF result as a string.
    return '\n'.join(atf)


if __name__ == '__main__':
    for name in sys.argv[1:]:
        with io.open(name, encoding='utf-8') as f:
            atf = convert(f)
            print(atf)
