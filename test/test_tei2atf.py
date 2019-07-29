import io

import tei2atf
import atf2tei


atf_filename = 'SIL-034.atf'
iliad = 'test/iliad.xml'


def test_roundtrip():
    '''Verify round-trip conversion to and from XML.'''
    with io.open(atf_filename, encoding='utf-8') as f:
        atf_sample = f.read()

    xml = atf2tei.convert(atf_sample)
    assert xml
    atf = tei2atf.convert(io.StringIO(str(xml)))
    assert atf
    xml = atf2tei.convert(atf)
    assert xml


def test_iliad():
    '''Verify conversion of an Iliad fragment.'''
    with io.open(iliad, encoding='utf-8') as f:
        atf = tei2atf.convert(f)
        assert atf
        assert atf.startswith('&greekLit:tlg0012.tlg001')
        assert 'lang grc' in atf
        assert '@Book 1' in atf
        assert '1. μῆνιν ἄειδε θεὰ' in atf
