'''Unit tests for generating Canonical Text Services index files.'''

import xml.etree.ElementTree as ET

import tei


def qualify(path):
    '''Expand each element in an XPath into a qname.'''
    result = []
    for tag in path.split('/'):
        qname = '{' + tei.namespace + '}' + tag
        result.append(qname)
    return '/'.join(result)


def test_bare():
    'Verify a bare document has a body element.'
    doc = tei.Document()
    xml = ET.fromstring(str(doc))
    assert xml.tag == qualify('TEI')
    assert len(xml.findall(qualify('text/body'))) == 1


def test_title():
    'Verify a base header has a title element.'
    header = tei.Header()
    xml = ET.fromstring(str(header))
    assert xml.tag == 'teiHeader'
    fileDesc = xml[0]
    assert fileDesc.tag == 'fileDesc'
    title = fileDesc[0][0]
    assert title.tag == 'title'
    # Header doesn't set a namespace attribute so no need to qualify.
    title = xml.find('fileDesc/titleStmt/title')
    assert title.tag == 'title'


def test_line():
    'Verify line serialization.'
    ref = '1'
    text = 'The quick brown fox jumped over the lazy dog'
    line = tei.Line(ref, text)
    xml = ET.fromstring(str(line))
    # Line doesn't set a namespace attribute so no need to qualify.
    assert xml.tag == 'l'
    assert xml.attrib['n'] == ref
    assert xml.text == text


def test_note():
    'Verify note serialization.'
    text = 'blank space'
    note = tei.Note(text)
    xml = ET.fromstring(str(note))
    assert xml.tag == 'note'
    assert xml.text == text


def test_document():
    'Verify basic attributes of a document are serialized.'
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
    title = xml.find(qualify('teiHeader/fileDesc/titleStmt/title'))
    assert title.text == name
    divs = xml.findall(qualify('text/body/div'))
    assert divs[0].attrib['type'] == 'edition'
    assert divs[1].attrib['type'] == 'translation'
