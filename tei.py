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
        'Construct an XML ElemenTree representation.'
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


class Text:
    '''Represents a TEI Text body.'''

    def __init__(self):
        self.type = 'edition'
