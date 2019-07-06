'''Unit tests for generating Canonical Text Services index files.'''

import xml.etree.ElementTree as ET

import tei


def qualify(path):
    '''Expand each element in an XPath into a qname'''
    result = []
    for tag in path.split():
        qname = '{' + tei.namespace + '}' + tag
        result.append(qname)
    return ' '.join(result)


def test_bare():
    doc = tei.Document()
    xml = ET.fromstring(str(doc))
    assert xml.tag == qualify('TEI')


def test_title():
    header = tei.Header()
    xml = ET.fromstring(str(header))
    assert xml.tag == 'teiHeader'


def test_document():
    name = 'Example Text Document'
    doc = tei.Document()
    doc.header = tei.Header()
    doc.header.title = name
    edition = tei.Edition()
    doc.parts.append(edition)
    translation = tei.Translation()
    translation.langauge = 'en'
    doc.parts.append(translation)
    xml = ET.fromstring(str(doc))
    assert xml.tag == qualify('TEI')
