import io
from itertools import repeat

import pytest

import atf2tei
import atf2cts


test_filename = 'SIL-034.atf'

atf_prefix = '''&X001001 = Text ATF snippet
#atf: lang akk
@tablet
@obverse
'''


def test_convert():
    '''Verify conversion of a test file.'''
    with io.open(test_filename, encoding='utf-8') as f:
        doc = atf2tei.convert(f.read())
        assert doc
        assert len(doc.parts) == 1


def test_segmentor_single():
    '''Verify segmentation of a test file.'''
    with io.open(test_filename, encoding='utf-8') as f:
        assert len(list(atf2cts.segmentor(f))) == 1


@pytest.mark.parametrize('count', range(4))
def test_segmentor(count):
    '''Verify segmentation of multiple blocks.

    Concatenate the test file with itself and check we get back
    the name number of copies.'''
    with io.open(test_filename, encoding='utf-8') as f:
        text = f.read()
    assert text

    multi = repeat(text, count)
    multi = '\n\n'.join(multi)
    multi = io.StringIO(multi)
    assert (len(list(atf2cts.segmentor(multi)))) == count


def test_note():
    '''Verify conversion of $-line annotations.'''

    # Append a $-line to the expected ATF header lines.
    ruling_text = 'double ruling'
    text = atf_prefix + f'$ {ruling_text}\n'
    # Convert.
    doc = atf2tei.convert(text)

    # Verify the conversion produced a single edition div.
    assert len(doc.parts) == 1
    edition = doc.parts[0]
    assert edition.type == 'edition'

    # Verify the edition has a single object TextPart.
    assert len(edition.children) == 1
    div = edition.children[0]
    assert div.type == 'textpart'
    assert div.name == 'tablet'

    # Verify the object has a single surface TextPart.
    assert len(div.children) == 1
    div = div.children[0]
    assert div.type == 'textpart'
    assert div.name == 'obverse'

    # Verify the surface has a single note child.
    assert len(div.children) == 1
    note = div.children[0]
    assert note.text == ruling_text
