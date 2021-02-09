from os import environ
from os.path import expanduser
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfFileWriter, PdfFileReader

from HandwrittenPage import HandwrittenPage
from ShelveReplacement import ShelveReplacement


load_dotenv(override=True)
DOCUMENT_DIR = Path(expanduser(environ['DOCUMENT_DIR']))

PDF_INCH_UNIT = 71.0
A4_SIZE = (8.27*PDF_INCH_UNIT, 11.69*PDF_INCH_UNIT)


class HandwrittenDocument:
    def __init__(self, name, create_new=False):
        self.name = name
        self.__path = DOCUMENT_DIR / (name+'.sqlite')
        self.__open_pages = {}

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
        key = '%03d' % item
        if key not in self.__open_pages:
            self.__open_pages[key] = HandwrittenPage(item, self.__shelve[key])
        return self.__open_pages[key]

    def __setitem__(self, item, hp):
        assert isinstance(hp, HandwrittenPage)
        key = '%03d' % item
        self.__shelve[key] = hp.get_strokes()
        self.__open_pages[key] = hp
        self.commit()

    def __delitem__(self, item):
        raise NotImplementedError()  # TODO!

    def append(self):
        hp = self[len(self)] = HandwrittenPage(len(self), strokes=[])
        self.commit()
        return hp

    def insert(self, index):
        raise NotImplementedError()  # TODO!

    def commit(self):
        self.__shelve.commit()

    def close(self):
        self.__shelve.close()

    def rename(self, new_name):
        # CHECK ME!!!!
        new_path = DOCUMENT_DIR / (new_name+'.sqlite')
        self.__path.rename(new_path)
        self.__path = new_path
        self.name = new_name

    def to_pdf(self):
        pdf = PdfFileWriter()

        for page_num in range(len(self)):
            data_out = BytesIO()
            _canvas = canvas.Canvas(data_out, pagesize=A4)
            _canvas.drawImage(ImageReader(self[page_num].get_image()),
                              0, 0, A4_SIZE[0], A4_SIZE[1])
            _canvas.save()
            page = PdfFileReader(BytesIO(data_out.getvalue())).getPage(0)
            pdf.addPage(page)

        out = BytesIO()
        pdf.write(out)
        return out

    def to_pdf_4_to_page(self):
        pdf = PdfFileWriter()

        _canvas = None
        data_out = None

        IMG_WIDTH = A4_SIZE[0]//2
        IMG_HEIGHT = A4_SIZE[1]//2

        IMG_HEADER = A4_SIZE[1]//5
        IMG_HEIGHT -= IMG_HEADER//2

        for page_num in range(len(self)):
            image = ImageReader(self[page_num].get_image())

            if page_num % 4 == 0:
                data_out = BytesIO()
                _canvas = canvas.Canvas(data_out, pagesize=A4)
                _canvas.setFont('Helvetica', 24)
                _canvas.drawCentredString(IMG_WIDTH, IMG_HEIGHT*2, self.name)

                _canvas.drawImage(image, 0,             A4_SIZE[1]//2, IMG_WIDTH, IMG_HEIGHT)
            elif page_num % 4 == 1:
                _canvas.drawImage(image, A4_SIZE[0]//2, A4_SIZE[1]//2, IMG_WIDTH, IMG_HEIGHT)
            elif page_num % 4 == 2:
                _canvas.drawImage(image, 0,             0,             IMG_WIDTH, IMG_HEIGHT)
            elif page_num % 4 == 3:
                _canvas.drawImage(image, A4_SIZE[0]//2, 0,             IMG_WIDTH, IMG_HEIGHT)

                _canvas.save()
                page = PdfFileReader(BytesIO(data_out.getvalue())).getPage(0)
                pdf.addPage(page)
                _canvas = None
            else:
                raise Exception()

        if _canvas:
            _canvas.save()
            page = PdfFileReader(BytesIO(data_out.getvalue())).getPage(0)
            pdf.addPage(page)

        out = BytesIO()
        pdf.write(out)
        return out
