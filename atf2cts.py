#!/usr/bin/env python3

import atf2tei


def segmentor(fp):
    'Read a file object and segment it into atf records.'
    atf = None
    sync = False
    for line in fp.readlines():
        if line.startswith('&'):
            print('-- New atf record: ', line.strip())
            # Start of a new record. Flush the old one, if any.
            if atf and sync:
                print('-- Yielding accumulated data.')
                yield atf
            atf = line
            sync = True
        else:
            atf += line
    if atf and sync:
        yield atf


if __name__ == '__main__':
    import io
    import os
    import sys

    from xml.dom.minidom import parseString
    from xml.parsers.expat import ExpatError

    data_path = 'data/test'
    os.makedirs(data_path, exist_ok=True)
    with io.open(os.path.join(data_path, '__cts__.xml'),
                 encoding='utf-8',
                 mode='w') as f:
        f.write('''<ti:textgroup xmlns:ti="http://chs.harvard.edu/xmlns/cts"
              urn="urn:cts:cdli:test">
  <ti:groupname xml:lang="eng">atf2tei test examples</ti:groupname>
</ti:textgroup>
''')

    for filename in sys.argv[1:]:
        print('-- Parsing:', filename)
        with io.open(filename, encoding='utf-8') as f:
            for atf in segmentor(f):
                xml = atf2tei.convert(atf)
                try:
                    dom = parseString(xml)
                except ExpatError as e:
                    print('Error parsing converted XML:')
                    print(xml)
                    raise e
                texts = dom.getElementsByTagName('text')
                assert len(texts) == 1
                text = texts[0]
                urn = text.getAttribute('n')
                lang = text.getAttribute('xml:lang')
                title = dom.getElementsByTagName('title')[0].firstChild.data
                print('-- title:', title)
                doc_basename = urn.split(':')[-1]
                doc_dirname = doc_basename.split('.')[-1]
                doc_path = os.path.join(data_path, doc_dirname)
                doc_filename = os.path.join(doc_path, doc_basename + '.' + lang + '.xml')
                print('-- Writing', urn, lang, 'to', doc_filename)
                os.makedirs(doc_path, exist_ok=True)
                with io.open(os.path.join(doc_path, '__cts__.xml'),
                             encoding='utf-8',
                             mode='w') as f:
                    f.write(f'''<ti:work
  xmlns:ti="http://chs.harvard.edu/xmlns/cts"
  groupUrn="urn:cts:cdli:test"
       urn="{urn}"
  xml:lang="{lang}">
  <ti:title xml:lang="akk">{atf2tei.escape(title)}</ti:title>
  <ti:edition
    workUrn="{urn}"
        urn="{urn}.{lang}"
  >
    <ti:label xml:lang="en">
      CDLI {doc_dirname} {atf2tei.escape(title)}
    </ti:label>
    <ti:description xml:lang="en">Test doc converted from atf.</ti:description>
  </ti:edition>
</ti:work>
''')
                with io.open(doc_filename, encoding='utf-8', mode='w') as f:
                    f.write(xml)
