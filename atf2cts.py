#!/usr/bin/env python3

import atf2tei
import cts


def segmentor(fp):
    'Read a file object and segment it into atf records.'
    atf = None
    sync = False
    for line in fp.readlines():
        if line.startswith('&'):
            print('-- New atf record: ', line.strip())
            # Start of a new record. Flush the old one, if any.
            if atf and sync:
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

    failed_parse = []
    failed_export = []
    success = 0
    data_path = 'data/test'
    os.makedirs(data_path, exist_ok=True)
    textgroup = cts.TextGroup()
    textgroup.urn = 'urn:cts:cdli:test'
    textgroup.name = 'atf2cts test examples'
    with io.open(os.path.join(data_path, '__cts__.xml'),
                 encoding='utf-8',
                 mode='w') as f:
        f.write(str(textgroup))

    for filename in sys.argv[1:]:
        print('-- Parsing:', filename)
        with io.open(filename, encoding='utf-8') as f:
            for atf in segmentor(f):
                try:
                    xml = atf2tei.convert(atf)
                except Exception as e:
                    print('Error converting ATF:')
                    print(atf)
                    failed_parse.append(atf)
                    continue
                try:
                    dom = parseString(xml)
                except Exception as e:
                    print('Error parsing converted XML:')
                    print(xml)
                    failed_export.append(xml)
                    continue
                texts = dom.getElementsByTagName('text')
                assert len(texts) == 1
                text = texts[0]
                urn = text.getAttribute('n')
                lang = text.getAttribute('xml:lang')
                title = dom.getElementsByTagName('title')[0].firstChild.data

                doc_basename = urn.split(':')[-1]
                doc_dirname = doc_basename.split('.')[-1]
                doc_path = os.path.join(data_path, doc_dirname)
                doc_filename = os.path.join(
                        doc_path, doc_basename + '.' + lang + '.xml')
                print('-- Writing', urn, lang, 'to', doc_filename)

                work = cts.Work()
                work.group_urn = textgroup.urn
                work.work_urn = urn
                work.language = lang
                work.description = 'Test doc converted from atf.'
                work.label = ' '.join(['CDLI', doc_dirname, title])
                work.title = title

                os.makedirs(doc_path, exist_ok=True)
                with io.open(os.path.join(doc_path, '__cts__.xml'),
                             encoding='utf-8',
                             mode='w') as f:
                    f.write(str(work))

                with io.open(doc_filename, encoding='utf-8', mode='w') as f:
                    f.write(xml)
                success += 1
        failed = len(failed_parse) + len(failed_export)
        ratio = 1 - failed/(failed + success)
        width = 50
        progress_bar = f"[{'='*int(width*ratio)}>{' '*int(width*(1-ratio))}]"
        print(f'  {progress_bar} {ratio * 100:3n}% success.')
        if failed_parse:
            print('Error:', len(failed_parse), 'records did not convert.')
        if failed_export:
            print('Error:', len(failed_export), 'records did not serialize.')
        print(f'Successfully converted {success} records from ATF.')
