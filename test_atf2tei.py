import io
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
