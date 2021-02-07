from os import environ
from pathlib import Path
from dotenv import load_dotenv

from HandwrittenPage import HandwrittenPage
from ShelveReplacement import ShelveReplacement


load_dotenv(override=True)
DOCUMENT_DIR = Path(environ['DOCUMENT_DIR'])


class HandwrittenDocument:
    def __init__(self, name):
        self.__name = name
        self.__path = DOCUMENT_DIR / (name+'.sqlite')
        self.__shelve = ShelveReplacement()

    def __len__(self):
        return len(self.__shelve)

    def __getitem__(self, item):
        return HandwrittenPage(self.__shelve['%03d' % item])

    def __setitem__(self, item):
        assert isinstance(item, HandwrittenPage)
        self.__shelve['%03d' % item] = item.get_strokes()

    def __delitem__(self, item):
        # TODO!
        del self.__shelve['%03d' % item]

    def commit(self):
        self.__shelve.commit()

    def close(self):
        self.__shelve.close()

    def rename(self, new_name):
        new_path = DOCUMENT_DIR / (new_name+'.sqlite')
        self.__path.rename(new_path)
        self.__path = new_path
        self.__name = new_name

    def to_pdf(self):
        pass

    def to_pdf_4_to_page(self):
        pass

