# atf2tei

This is a tool for converting [ATF](http://oracc.museum.upenn.edu/doc/help/editinginatf/),
a text markup format used by the [Cuneiform Digital Library Initiative](https://cdli.ucla.edu)
to describe inscriptions on clay tablets and other artefacts,
and [TEI](https://tei-c.org), an [XML](https://en.wikipedia.org/wiki/XML)
markup format used by the Text Encoding Initiative for digital representation
of scholarly texts.

It is intended as part of an interface to make the CDLI and related
databases more accessible.

The project was originally written as part of a Google
[Summer of Code](https://summerofcode.withgoogle.com/)
project in 2019.

## Getting Started

    ```
    pipenv install
    pipenv run python atf2tei.py SIL-034.atf
    ```

The first line sets up a python virtual environment and installs
the dependencies. It only needs to be run once.
The second converts the included atf text file to tei.
