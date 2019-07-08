'''Models for generating Canonical Text Services index files.'''

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString


class TextGroup:
    '''Represents a textgroup element.'''

    ns = {'ti': 'http://chs.harvard.edu/xmlns/cts'}

    def __init__(self):
        self.urn = None
        self.name = None

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

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


class Work:
    '''Represents a TEI work.'''

    ns = {'ti': 'http://chs.harvard.edu/xmlns/cts'}

    def __init__(self):
        self.group_urn = None
        self.work_urn = None
        self.language = None
        self.description = None
        self.label = None
        self.title = None

    def __str__(self):
        'Serialized XML representation as a string.'
        serialized = ET.tostring(self.xml, encoding='unicode')
        return parseString(serialized).toprettyxml()

    @property
    def xml(self):
        'Construct an XML ElementTree representation of member data.'
        xml = ET.Element('ti:work')
        xml.set('xmlns:ti', self.ns['ti'])
        if self.language:
            xml.set('xml:lang', self.language)
        title = ET.SubElement(xml, 'ti:title')
        title.text = self.title
        title.set('xml:lang', 'eng')
        edition = ET.SubElement(xml, 'ti:edition')
        if self.group_urn:
            xml.set('groupUrn', self.group_urn)
        if self.work_urn:
            xml.set('urn', self.work_urn)
            edition.set('workUrn', self.work_urn)
            edition.set('urn', self.work_urn + '.' + self.language)
        label = ET.SubElement(edition, 'ti:label')
        if self.label:
            label.text = self.label
            label.set('xml:lang', 'eng')
        description = ET.SubElement(edition, 'ti:description')
        if self.description:
            description.text = self.description
            description.set('xml:lang', 'eng')
        return xml
