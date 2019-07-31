#!/usr/bin/env python3

import os
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
            print('New atf record:', line.strip())
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


def convert(atf, data_path, textgroup=None):
    '''Convert an atf string and write it out as XML.

    data_path should be the path to the data directory inside
    the target CTS file repository.

    The URNs and file locations under data_path will be derived
    from the textgroup, if one is passed in. If no textgroup is
    supplied, a work-specific textgroup will be generated and
    written out as well.

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
        return export_failed

    if not textgroup:
        'Generate a work-specific textgroup.'
        textgroup = cts.TextGroup()
        textgroup.urn = f'urn:cts:cdli:{doc.header.cdli_code}'
        textgroup.name = f'CDLI {doc.header.cdli_code} {doc.header.title}'
        data_path = os.path.join(data_path, textgroup.urn.split(':')[-1])
        os.makedirs(data_path, exist_ok=True)
        print(f'Writing textgroup to {data_path}')
        os.makedirs(data_path, exist_ok=True)
        textgroup.write(os.path.join(data_path, '__cts__.xml'))

    # Compose work metadata under the given textgroup.
    urn = f'{textgroup.urn}.{doc.header.cdli_code}'

    work = cts.Work()
    work.groupUrn = textgroup.urn
    work.workUrn = urn
    work.language = doc.language
    work.title = doc.header.title
    work.label = f'CDLI {doc.header.cdli_code} {work.title}'
    work.description = 'Cuneiform transcription converted from atf.'

    work_path = os.path.join(data_path, urn.split('.')[-1])

    print('Writing', urn, doc.language, 'to', work_path)
    os.makedirs(work_path, exist_ok=True)
    work.write(os.path.join(work_path, '__cts__.xml'))

    # Add CTS refsDecl.
    encodingDesc = ET.Element('encodingDesc')
    encodingDesc.append(cts.RefsDecl().xml)
    doc.header.encodingDesc = encodingDesc

    # Write out each part of the document parts separately
    # (edition, translation, etc.) so they can be referenced
    # individually through the CTS refsDecl.
    parts = doc.parts
    for part in parts:
        # Set urn, language per CTS epidoc guidelines.
        if isinstance(part, tei.Edition):
            part.name = f'{work.workUrn}.cdli-{work.language}'
            part.language = work.language
        elif isinstance(part, tei.Translation):
            part.name = f'{work.workUrn}.cdli-{part.language}'
        else:
            print('Skipping unhandled document part', part)
            continue

        doc.parts = [part]

        doc_filename = part.name.split(':')[-1] + '.xml'
        doc.write(os.path.join(work_path, doc_filename))

    return success


if __name__ == '__main__':
    import io
    import sys

    from concurrent import futures
    from datetime import datetime

    start = datetime.utcnow()
    successful = 0
    parse_failures = 0
    export_failures = 0

    # Relative path to place CTS file repository data.
    data_path = 'data'

    for filename in sys.argv[1:]:
        print('Parsing:', filename)
        with io.open(filename, encoding='utf-8') as f:
            with futures.ProcessPoolExecutor() as exe:
                jobs = [exe.submit(convert, atf, data_path)
                        for atf in segmentor(f)]
                for job in futures.as_completed(jobs):
                    s, p, e = job.result()
                    successful += s
                    parse_failures += p
                    export_failures += e
    if parse_failures:
        print('Error:', parse_failures, 'records did not convert.')
    if export_failures:
        print('Error:', export_failures, 'records did not serialize.')
    elapsed = datetime.utcnow() - start
    seconds = elapsed.seconds + elapsed.microseconds*1e-6
    print(f'Successfully converted {successful} records from ATF',
          f'in {seconds:0.3f} seconds.')
