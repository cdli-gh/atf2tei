#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape

from pyoracc.atf.common.atffile import AtfFile
from pyoracc.model.line import Line
from pyoracc.model.oraccobject import OraccObject
from pyoracc.model.ruling import Ruling
from pyoracc.model.state import State
from pyoracc.model.translation import Translation

import tei

verbose = False


def convert(atf_text):
    """
    Create a TEI representation of a file-like object containing ATF.
    """

    # Parse the ATF input string.
    atf = AtfFile(atf_text, 'cdli', False)
    if verbose:
        print("Parsed {} -- {}".format(atf.text.code, atf.text.description))

    # Construct a TEI Document to hold the converted text.
    doc = tei.Document()
    doc.language = atf.text.language
    doc.header = tei.Header()
    doc.header.title = atf.text.description
    doc.header.cdli_code = atf.text.code

    # Traverse the parse tree, recording lines under labels.
    translations = {}
    objects = [item for item in atf.text.children
               if isinstance(item, OraccObject)]
    edition = tei.Edition()
    doc.parts.append(edition)
    for item in objects:
        part = tei.TextPart(item.objecttype)
        edition.append(part)
        for section in item.children:
            if isinstance(section, OraccObject):
                try:
                    name = section.name
                except AttributeError:
                    name = section.objecttype
                div = tei.TextPart(name)
                part.append(div)
            elif isinstance(section, Translation):
                # Handle in another pass.
                continue
            else:
                print('Skipping unknown section type',
                      type(section).__name__)
                continue
            for obj in section.children:
                if isinstance(obj, Line):
                    text = normalize_transliteration(obj.words)
                    line = tei.Line(obj.label, text)
                    div.append(line)
                    # Older pyoracc parses interlinear translatsions
                    # as notes. Remember them for serialization below.
                    for note in obj.notes:
                        if note.content.startswith('tr.'):
                            lang, text = note.content.split(':', maxsplit=1)
                            _, lang = lang.split('.')
                            # tr.ts is used for normalization, so mark
                            # this with the primary object's language.
                            if lang == 'ts':
                                lang == atf.text.language
                            tr_line = Line(obj.label)
                            tr_line.words = text.strip().split()
                            if lang not in translations:
                                translations[lang] = []
                            translations[lang].append(tr_line)
                elif isinstance(obj, State) or isinstance(obj, Ruling):
                    text = str(obj).strip()
                    # Strip the initial '$' off the ATF representation.
                    text = text[1:].strip()
                    div.append(tei.Note(text))
                else:
                    print('Skipping unknown section child type',
                          type(obj).__name__)
                    continue

    # Add accumulated interlinear translations to the document.
    for lang, tr_lines in translations.items():
        translation = tei.Translation()
        translation.language = lang
        doc.parts.append(translation)
        for tr_line in tr_lines:
            text = ' '.join(tr_line.words)
            line = tei.Line(tr_line.label, text)
            translation.append(line)

    # Traverse the tree again, recording any parallel translation sections.
    # pyoracc only supports these for English.
    translation = tei.Translation()
    translation.language = 'eng'
    translation_empty = True
    for item in objects:
        part = tei.TextPart(item.objecttype)
        translation.append(part)
        for section in item.children:
            # Skip anything which is not a translation for this pass.
            if not isinstance(section, Translation):
                continue
            for surface in section.children:
                if isinstance(surface, OraccObject):
                    div = tei.TextPart(surface.objecttype)
                    part.append(div)
                    for obj in surface.children:
                        if isinstance(obj, Line):
                            text = ' '.join(obj.words)
                            line = tei.Line(obj.label, text)
                            div.append(line)
                            translation_empty = False
                        else:
                            print('Skipping unknown section child type',
                                  {type(obj).__name__})
                            continue
    if not translation_empty:
        doc.parts.append(translation)

    return doc


def normalize_transliteration(words):
    'Convert a sequence of words from atf to standard formatting.'
    # See http://oracc.org/doc/help/editinginatf/primer/inlinetutorial/
    result = []
    for word in words:
        # Convert digraphs to corresponding unicode characters.
        word = re.sub(r'sz', 'š', word)     # \u0161
        word = re.sub(r'SZ', 'Š', word)     # \u0160
        word = re.sub(r's,', 'ṣ', word)     # \u1E63
        word = re.sub(r'S,', 'Ṣ', word)     # \u1E62
        word = re.sub(r't,', 'ṭ', word)     # \u1E6D
        word = re.sub(r'T,', 'Ṭ', word)     # \u1E6C
        word = re.sub(r's\'', 'ś', word)    # \u015B
        word = re.sub(r'S\'', 'Ś', word)    # \u015A
        word = re.sub(r'h,', 'ḫ', word)     # \u1E2B
        word = re.sub(r'H,', 'Ḫ', word)     # \u1E2A
        word = re.sub(r'j', 'ŋ', word)      # \u014B
        word = re.sub(r'J', 'Ŋ', word)      # \u014A
        # Convert damage marks to half-brackets.
        marked = [
            '⸢' + sign[:-1] + '⸣' if sign.endswith('#')
            else sign
            for sign in word.split('-')
        ]
        word = '-'.join(marked)
        # XML-escape the result.
        word = escape(word)
        # Convert markup to tei elements.
        # TODO: <c type="determinative">
        # TODO: <c type="sign" subtype="logo">
        result.append(word)
    return ' '.join(result)


if __name__ == '__main__':
    import io
    import sys
    for filename in sys.argv[1:]:
        with io.open(filename, encoding='utf-8') as f:
            doc = convert(f.read())
            print(doc)
