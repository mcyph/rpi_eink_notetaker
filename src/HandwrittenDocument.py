from os import environ
from os.path import expanduser
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfFileWriter, PdfFileReader

from HandwrittenPage import HandwrittenPage
from ShelveReplacement import ShelveReplacement


load_dotenv(override=True)
DOCUMENT_DIR = Path(expanduser(environ['DOCUMENT_DIR']))

PDF_INCH_UNIT = 71.0
A4_SIZE = (8.27*PDF_INCH_UNIT, 11.69*PDF_INCH_UNIT)


class HandwrittenDocument:
    def __init__(self, name, create_new=False):
        self.__name = name
        self.__path = DOCUMENT_DIR / (name+'.sqlite')

        if not create_new and not self.__path.exists():
            raise FileNotFoundError(self.__path)

        self.__shelve = ShelveReplacement(self.__path)

        if create_new:
            # Add an initial page if new
            self.append()

    def __del__(self):
        try:
            self.__shelve.commit()
            self.__shelve.close()
        except:
            pass

    def __len__(self):
        return len(self.__shelve)

    def __getitem__(self, item):
        return HandwrittenPage(item, self.__shelve['%03d' % item])

    def __setitem__(self, item):
        assert isinstance(item, HandwrittenPage)
        self.__shelve['%03d' % item] = item.get_strokes()

    def __delitem__(self, item):
        raise NotImplementedError()  # TODO!

    def append(self):
        hp = self[len(self)] = HandwrittenPage(len(self), strokes=[])
        return hp

    def insert(self, index):
        raise NotImplementedError()  # TODO!

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
        pdf = PdfFileWriter()

        for page_num in range(len(self)):
            data_out = BytesIO()
            _canvas = canvas.Canvas(data_out, pagesize=A4)
            _canvas.drawImage(self[page_num].get_image(),
                              0, 0, A4_SIZE[0], A4_SIZE[1])
            _canvas.save()
            page = PdfFileReader(BytesIO(data_out.getvalue())).getPage(0)
            pdf.addPage(page)

        out = BytesIO()
        pdf.write(out)
        return out

    def to_pdf_4_to_page(self):
        pass

