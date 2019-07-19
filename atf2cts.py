#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

import atf2tei
import cts
import tei


def segmentor(fp):
    'Read a file object and segment it into atf records.'
    atf = None
    sync = False
    for line in fp.readlines():
        if line.startswith('&'):
            print('New atf record: ', line.strip())
            # Start of a new record. Flush the old one, if any.
            if atf and sync:
                yield atf
            atf = line
            sync = True
        elif not atf:
            print('WARNING: skipping unrecognized line:', line.strip())
            continue
        else:
            atf += line
    if atf and sync:
        yield atf


def convert(atf, textgroup, data_path):
    '''Convert an atf string and write it out as XML.

    returns a (success, parse_failed, export_failed) flag tuple.'''
    success = (True, False, False)
    parse_failed = (False, True, False)
    export_failed = (False, False, True)
    try:
        doc = atf2tei.convert(atf)
    except Exception as e:
        print('Error converting ATF:', e)
        print(atf)
        return parse_failed
    try:
        _ = parseString(str(doc))
    except Exception as e:
        print('Error parsing converted XML:', e)
        print(doc)
        return export_failed

    # Compose work metadata under the given textgroup.
    urn = f'{textgroup.urn}.{doc.header.cdli_code}'

    work = cts.Work()
    work.groupUrn = textgroup.urn
    work.workUrn = urn
    work.language = doc.language
    work.title = doc.header.title
    work.label = f'CDLI {doc.header.cdli_code} {work.title}'
    work.description = 'Test doc converted from atf.'

    work_path = os.path.join(data_path, urn.split('.')[-1])

    print('Writing', urn, doc.language, 'to', work_path)
    os.makedirs(work_path, exist_ok=True)
    work.write(os.path.join(work_path, '__cts__.xml'))

    # Set Edition urn per CTS epidoc guidelines.
    editionUrn = f'{work.workUrn}.cdli-{work.language}'
    for obj in doc.parts:
        if isinstance(obj, tei.Edition):
            obj.name = editionUrn
            obj.language = work.language

    # Add CTS refsDecl.
    encodingDesc = ET.Element('encodingDesc')
    encodingDesc.append(cts.RefsDecl().xml)
    doc.header.encodingDesc = encodingDesc

    doc_filename = editionUrn.split(':')[-1] + '.xml'
    doc.write(os.path.join(work_path, doc_filename))

    return success


if __name__ == '__main__':
    import io
    import os
    import sys

    from concurrent import futures
    from datetime import datetime

    start = datetime.utcnow()
    failed_parse = []
    failed_export = []
    successful = 0
    parse_failures = 0
    export_failures = 0

    textgroup = cts.TextGroup()
    textgroup.urn = 'urn:cts:cdli:test'
    textgroup.name = 'Test samples converted by atf2cts'
    data_path = os.path.join('data', textgroup.urn.split(':')[-1])
    os.makedirs(data_path, exist_ok=True)
    print(f'Writing textgroup to {data_path}')
    os.makedirs(data_path, exist_ok=True)
    textgroup.write(os.path.join(data_path, '__cts__.xml'))

    for filename in sys.argv[1:]:
        print('Parsing:', filename)
        with io.open(filename, encoding='utf-8') as f:
            with futures.ProcessPoolExecutor() as exe:
                jobs = [exe.submit(convert, atf, textgroup, data_path)
                        for atf in segmentor(f)]
                for job in futures.as_completed(jobs):
                    s, p, e = job.result()
                    successful += s
                    parse_failures += p
                    export_failures += e
    if parse_failures:
        print('Error:', parse_failures, 'records did not convert.')
    if failed_export:
        print('Error:', export_failures, 'records did not serialize.')
    elapsed = datetime.utcnow() - start
    seconds = elapsed.seconds + elapsed.microseconds*1e-6
    print(f'Successfully converted {successful} records from ATF',
          f'in {seconds:0.3f} seconds.')
