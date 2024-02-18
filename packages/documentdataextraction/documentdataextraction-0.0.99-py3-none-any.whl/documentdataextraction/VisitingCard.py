import cv2
import pytesseract
import re
from kraken import binarization
from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from pdf2image import convert_from_path
import loggerutility as logger

# pytesseract.pytesseract.tesseract_cmd = 'E:/tes/tesseract.exe'

class visitingCard:

# Name extraction code (Name must be in left side)
    def get_full_name(self,lst):
        name1 = r"([a-zA-Z'.,-]+( [a-zA-Z'.,-]+)*){8,30}"
        full_name1 = re.search(name1, lst)

        if full_name1 is not None:
            return full_name1.group()


    # Email Id extraction code
    def get_email(self,lst):
        mail_pattern = r'\b[A-Za-z0-9. _%+-]+@[A-Za-z0-9. -]+\.[A-Z|a-z ]{2,3}'

        mail = re.search(mail_pattern, lst.replace(" ", "").replace("-", "."))
        if mail is not None:
            return mail.group()


    # contact number extraction code
    def get_phone_number(self,lst):
        contact_no4 = r'[0-9.]{13}\b'
        contact_no1 = r'[0-9]{10}\b'
        contact_no3 = r'[0-9.]{12}\b'
        contact_no2 = r'[0-9.]{11}\b'
        Contact_NO1 = re.search(contact_no1,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO1 is not None:
            logger.log('10','0')
            return Contact_NO1.group()
        Contact_NO2 = re.search(contact_no2,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO2 is not None:
            logger.log('11','0')
            return Contact_NO2.group()
        Contact_NO3 = re.search(contact_no3,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO3 is not None:
            logger.log('12','0')
            return Contact_NO3.group()
        Contact_NO4 = re.search(contact_no4,
                                lst.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("@",
                                                                                                                "").replace(
                                    "*", ""))
        if Contact_NO4 is not None:
            logger.log('13','0')
            return Contact_NO4.group()


    # website extraction code
    def get_website(self,lst):
        website_pattern = r'\b(WWW|www)+.[A-Za-z0-9. _%+-]+\.[A-Z|a-z]{2,3}\b'
        web = re.search(website_pattern, lst.replace(" ", ""))
        if web is not None:
            return web.group()


    def pdf_data_extractor(self,PDF_file):
        image_file_list = []
        with TemporaryDirectory() as tempdir:
        
            pdf_pages = convert_from_path(PDF_file, 500)
                
            # Read in the PDF file at 500 DPI

            # Iterate through all the pages stored above
            for page_enumeration, page in enumerate(pdf_pages, start=1):
            
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for image_file in image_file_list:
                text = str(((pytesseract.image_to_string(Image.open(image_file)))))
                

            return text


    # Accept the file for for data extraction



    def extract(self, File_path):
        name = File_path.split(".")
        logger.log(f"{name[1]}","0")
        if name[1] == "PDF" or name[1] == "pdf":
            OCR_Text = self.pdf_data_extractor(File_path)
            logger.log(f"Visiting card OCR ::: {OCR_Text}","0")
        else:
            im = Image.open(File_path)
            bw_im = binarization.nlbin(im)
            d = decode(bw_im, symbols=[ZBarSymbol.QRCODE])
            if d:
                for i in d:
                    logger.log("QR code Exicuted","0")
                    OCR_Text = i.data.decode('utf-8')

                    OCR_Text = OCR_Text.replace(";", " ")
                    # logger.log(f"{OCR_Text}","0")
            else:
                path = File_path
                image = cv2.imread(path, 0)
                OCR = pytesseract.image_to_string(image)
                # logger.log("f{len(OCR)}","0")
                # logger.log(f"{OCR}","0")
                logger.log(f"{OCR}","0")
                OCR_Text = OCR
        Name = ""
        Telephone = ""
        Email = ""
        Website = ""
        result = {}
        # ===========
        Final_text = {  "Name"      : self.get_full_name(OCR_Text),
                        "Telephone" : self.get_phone_number(OCR_Text),
                        "Email"     : self.get_email(OCR_Text),
                        "Website"   : self.get_website(OCR_Text)        
                    }
        
        # logger.log(f"{Final_text}","0")
        result["name"]       =  Final_text["Name"]
        result["tele1"]      =  Final_text["Telephone"]
        result["email_addr"] =  Final_text["Email"]
        result["Website"]    =  Final_text["Website"]
        logger.log(f"Visiting card result ::: {result}\n\n")

        return result