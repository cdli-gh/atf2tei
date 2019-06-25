import io
import atf2tei
import atf2cts


def test_convert():
    with io.open("SIL-034.atf", encoding='utf-8') as f:
        xml = atf2tei.convert(f.read())
        assert xml


def test_cts():
    with io.open("SIL-034.atf", encoding='utf-8') as f:
        assert len(list(atf2cts.segmentor(f))) == 1
