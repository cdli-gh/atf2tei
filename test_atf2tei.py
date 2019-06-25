import io
from itertools import repeat

import pytest

import atf2tei
import atf2cts


test_filename = 'SIL-034.atf'


def test_convert():
    '''Verify conversion of a test file.'''
    with io.open(test_filename, encoding='utf-8') as f:
        xml = atf2tei.convert(f.read())
        assert xml


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
