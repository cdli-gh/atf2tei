'''Unit tests for generating Canonical Text Services index files.'''

import xml.etree.ElementTree as ET

from cts import TextGroup
from cts import Work


def test_bare():
    group = TextGroup()
    xml = ET.fromstring(str(group))
    qname = '{' + TextGroup.ns['ti'] + '}textgroup'
    assert xml.tag == qname


def test_urn():
    urn = 'urn:cts:cdli:test.faketext'
    group = TextGroup()
    group.urn = urn
    xml = ET.fromstring(str(group))
    assert xml.tag == '{' + TextGroup.ns['ti'] + '}textgroup'
    assert xml.get('urn') == urn


def test_group():
    name = 'Example Text Group'
    urn = 'urn:cts:cdli:test.example'
    group = TextGroup()
    group.name = name
    group.urn = urn
    xml = ET.fromstring(str(group))
    element = xml.find('ti:groupname', TextGroup.ns)
    assert element.text == name
    assert xml.tag == '{' + TextGroup.ns['ti'] + '}textgroup'
    assert xml.get('urn') == urn


def test_work():
    work = Work()
    print(work)
    assert work.xml
