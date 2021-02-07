from os import environ
from os.path import expanduser
from pathlib import Path
from dotenv import load_dotenv

from HandwrittenDocument import HandwrittenDocument


load_dotenv(override=True)
DOCUMENT_DIR = Path(expanduser(environ['DOCUMENT_DIR']))


def _sanitize(item):
    item = ''.join(i for i in item if i not in '<>:"/\\|?*').strip()
    return item


class HandwrittenDocuments:
    def __init__(self):
        self.__open_docs = {}

    def __iter__(self):
        for i in DOCUMENT_DIR.glob('*.sqlite'):
            yield i.name[:-7]

    def __getitem__(self, item):
        item = _sanitize(item)
        if item not in self.__open_docs:
            self.__open_docs[item] = HandwrittenDocument(item)
        return self.__open_docs[item]

    def __contains__(self, item):
        item = _sanitize(item)
        return item in list(self)

    def create_new(self, item):
        item = _sanitize(item)
        assert item not in self
        hd = self.__open_docs[item] = HandwrittenDocument(item, create_new=True)
        return hd
