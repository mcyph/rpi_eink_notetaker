from os import environ
from pathlib import Path
from dotenv import load_dotenv

from HandwrittenDocument import HandwrittenDocument


load_dotenv(override=True)
DOCUMENT_DIR = Path(environ['DOCUMENT_DIR'])


class HandwrittenDocuments:
    def __init__(self):
        self.__open_docs = {}

    def __iter__(self):
        for i in DOCUMENT_DIR.glob('*.sqlite'):
            yield i[:-7]

    def __getattr__(self, item):
        return HandwrittenDocument(item)

