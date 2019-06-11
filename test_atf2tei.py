import io
import atf2tei


def test_convert():
    with io.open("SIL-034.atf", encoding='utf-8') as f:
        xml = atf2tei.convert(f)
        assert xml
