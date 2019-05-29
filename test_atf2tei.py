import atf2tei


def test_convert():
    with open("SIL-034.atf") as f:
        xml = atf2tei.convert(f)
        assert xml
