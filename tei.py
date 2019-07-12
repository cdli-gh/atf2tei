'''Models for generating Epidoc Text Encoding Initiative xml files.'''

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

namespace = 'http://www.tei-c.org/ns/1.0'


class Document:
    '''Represents a TEI document.'''

    def __init__(self):
        self.header = None
        self.parts = []

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

    @property
    def xml(self):
        'Construct an XML representation of member data.'
        xml = ET.Element('TEI')
        xml.set('xmlns', namespace)
        if self.header:
            xml.append(self.header.xml)
        text = ET.SubElement(xml, 'text')
        body = ET.SubElement(text, 'body')
        for part in self.parts:
            body.append(part.xml)
        return xml


class Header:
    '''Represents a TEI Header.'''

    def __init__(self):
        self.title = None
        self.publication = 'Converted from ATF by atf2tei.'
        self.cdli_code = None

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

    @property
    def xml(self):
        'Construct an XML ElementTree representation of member data.'
        xml = ET.Element('teiHeader')
        fileDesc = ET.SubElement(xml, 'fileDesc')
        titleStmt = ET.SubElement(fileDesc, 'titleStmt')
        title = ET.SubElement(titleStmt, 'title')
        title.text = self.title
        if self.publication:
            publicationStmt = ET.SubElement(fileDesc, 'publicationStmt')
            p = ET.SubElement(publicationStmt, 'p')
            p.text = self.publication
        if self.cdli_code:
            sourceDesc = ET.SubElement(fileDesc, 'sourceDesc')
            bibl = ET.SubElement(sourceDesc, 'bibl')
            title = ET.SubElement(bibl, 'title')
            title.text = 'CDLI'
            idno = ET.SubElement(title, 'idno')
            idno.set('type', 'CDLI')
            idno.text = self.cdli_code
        return xml


class TextPart:
    '''Represents an Epidoc text division.'''

    def __init__(self):
        self.name = None
        self.type = 'textpart'
        self.children = []

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

    @property
    def xml(self):
        'Construct an XML ElementTree representation.'
        xml = ET.Element('div')
        xml.set('type', self.type)
        if self.name:
            xml.set('n', self.name)
        for child in self.children:
            xml.append(child.xml)
        return xml


class Edition(TextPart):
    '''Represents and Epidoc text edition.'''

    def __init__(self):
        super().__init__()
        self.type = 'edition'


class Translation(TextPart):
    '''Represents and Epidoc text translation.'''

    def __init__(self):
        super().__init__()
        self.type = 'translation'
        self.language = None

    @property
    def xml(self):
        xml = super().xml
        if self.language:
            xml.set('xml:lang', self.language)
        return xml


class Line:
    '''Represents a line of text.'''
    def __init__(self, ref, content):
        self.ref = ref
        self.content = content

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

    @property
    def xml(self):
        'Construct an XML ElementTree representation.'
        xml = ET.Element('l')
        xml.set('n', self.ref)
        xml.text = self.content
        return xml
