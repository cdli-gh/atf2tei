'''Models for generating Canonical Text Services index files.'''

import xml.etree.ElementTree as ET

from tei import XMLSerializer


class TextGroup(XMLSerializer):
    '''Represents a CTS textgroup element.'''

    ns = {'ti': 'http://chs.harvard.edu/xmlns/cts'}

    def __init__(self):
        self.urn = None
        self.name = None

    @property
    def xml(self):
        'Construct an XML representation of member data.'
        xml = ET.Element('ti:textgroup')
        xml.set('xmlns:ti', self.ns['ti'])
        if self.urn:
            xml.set('urn', self.urn)
        if self.name:
            groupname = ET.Element('ti:groupname')
            groupname.set('xml:lang', 'eng')
            groupname.text = self.name
            xml.append(groupname)
        return xml


class Work(XMLSerializer):
    '''Represents a CTS work.'''

    ns = {'ti': 'http://chs.harvard.edu/xmlns/cts'}

    def __init__(self):
        self.groupUrn = None
        self.workUrn = None
        self.language = None
        self.title = None
        self.parts = []

    @property
    def xml(self):
        'Construct an XML ElementTree representation of member data.'
        xml = ET.Element('ti:work')
        xml.set('xmlns:ti', self.ns['ti'])
        if self.groupUrn:
            xml.set('groupUrn', self.groupUrn)
        if self.workUrn:
            xml.set('urn', self.workUrn)
        if self.language:
            xml.set('xml:lang', self.language)
        title = ET.SubElement(xml, 'ti:title')
        title.text = self.title
        title.set('xml:lang', 'eng')

        for part in self.parts:
            if part.type == 'edition':
                textElement = ET.SubElement(xml, 'ti:edition')
                # ti:edition inherits the language of the ti:work element.
            elif part.type == 'translation':
                textElement = ET.SubElement(xml, 'ti:translation')
                # Translations have their own languages.
                textElement.set('xml:lang', part.language)

            if self.workUrn:
                textElement.set('workUrn', self.workUrn)
                urn = self.workUrn + '.cdli'
                if part.language:
                    urn += '-' + part.language
                textElement.set('urn', urn)

            labelElement = ET.SubElement(textElement, 'ti:label')
            labelElement.text = part.label
            labelElement.set('xml:lang', 'mul')

            descriptionElement = ET.SubElement(textElement, 'ti:description')
            descriptionElement.text = part.description
            descriptionElement.set('xml:lang', 'eng')

        return xml


class RefsDecl(XMLSerializer):
    '''Produce the refsDecl subtree required by CTS guidelines.

    Results are specific to the way we structure cuneiform
    data from ATF.'''
    prefix = '#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div'
    levels = [
        (
          'line', 2,
          'This pattern references a specific line.',
          prefix + "/tei:div[@n='$1']/tei:l[@n='$2'])"
        ),
        (
          'surface', 1,
          'This pattern references an inscribed surface on an object.',
          prefix + "/tei:div[@n='$1'])"
        ),
    ]

    @property
    def xml(self):
        'Construct an XML ElementTree representation of member data.'
        refsDecl = ET.Element('refsDecl')
        refsDecl.set('n', 'CTS')
        for name, count, description, xpath in self.levels:
            pattern = ET.SubElement(refsDecl, 'cRefPattern')
            pattern.set('n', name)
            pattern.set('matchPattern', r'\.'.join([r'(\w+)'] * count))
            pattern.set('replacementPattern', xpath)
            p = ET.SubElement(pattern, 'p')
            p.text = description
        return refsDecl
