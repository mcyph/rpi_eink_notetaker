from os import environ
from os.path import expanduser
from pathlib import Path
from dotenv import load_dotenv

from HandwrittenDocument import HandwrittenDocument


load_dotenv(override=True)
DOCUMENT_DIR = Path(expanduser(environ['DOCUMENT_DIR']))


class HandwrittenDocuments:
    def __init__(self):
        self.__open_docs = {}

    def __iter__(self):
        for i in DOCUMENT_DIR.glob('*.sqlite'):
            yield i[:-7]

    def __getattr__(self, item):
        item = ''.join(i for i in item if i not in '<>:"/\\|?*').strip()
        if item not in self.__open_docs:
            self.__open_docs[item] = HandwrittenDocument(item)
        return self.__open_docs[item]

    def create_new(self, item):
        item = ''.join(i for i in item if i not in '<>:"/\\|?*').strip()
        return HandwrittenDocument(item, create_new=True)
