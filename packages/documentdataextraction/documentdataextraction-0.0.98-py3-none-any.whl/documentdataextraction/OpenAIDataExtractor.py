import requests, json, traceback, openai
import os
from invoice2data import extract_data
from flask import request
import loggerutility as logger
from PIL import Image
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path
import cv2
import pytesseract
import yaml
from .GenerateExtractTemplate import GenerateExtractTemplate
import pdfplumber
import pdftotext
import datetime
import docx2txt
import pandas as pd
import pathlib
from striprtf.striprtf import rtf_to_text
import unicodedata
import tiktoken
import commonutility as common
import ast
import PyPDF2
import json
import base64
import requests
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import io
from PIL import Image
import pdfkit
 
class OpenAIDataExtractor:

    mainPg_Instruction    =  ""
    otherPg_Instruction   =  ""
    fileExtension_lower   =  ""
    userId                =  ""
    processing_method     =  ""
    textFile_Path         =  ""  
    file_storage_path     =  os.environ.get('de_storage_path', '/flask_downloads')

    def pytesseract_ocr(self,PDF_file):
        image_file_list     =  []
        dict                =  {}
        
        logger.log(f"pytesseract_ocr filename ::: {PDF_file}\n{type(PDF_file)} \n")
        with TemporaryDirectory() as tempdir:
            pdf_pages = convert_from_path(PDF_file, 500)
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg" 
                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for page_no,image_file in enumerate(image_file_list): 
                text = cv2.imread(image_file)
                image_file = self.resizing(text, 50)
                dict[str(page_no+1)] = str(((pytesseract.image_to_string(image_file)))).strip()

            logger.log(f"pytesseract for image ::::: {dict}","0") 

            self.textFile_Path = PDF_file[ : -3] + "txt"
            logger.log(f" textFile_Path ::: {self.textFile_Path}\n")
            with open(self.textFile_Path ,"w") as txt_fileObj :
                txt_fileObj.write("\n".join(dict.values()))
                logger.log(f"\nfileObj::: {txt_fileObj}\n")

            file_path = self.txt_To_Pdf(self.textFile_Path)

            return dict, file_path 
        
    def pdfplumber_ocr(self,PDF_file):
        OCR_lst = []
        ocr_text_final = ""
        dict = {}
        
        file = pdfplumber.open(PDF_file)
        ocr_text = file.pages
        logger.log(f"file.pages::: {file.pages}", "0")
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            dict[str(page_no+1)] = ocr_text_final.strip()
            # OCR_lst.append(ocr_text_final)
        # print(len(dict.values()))
        # print(dict)
        return dict
    
    def pdftotext_ocr(self,PDF_file):
        with open(PDF_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        OCR_Text = "\n\n".join(pdf)
        return OCR_Text
    
    def gaussianBlur(self,img,blur_value):
        logger.log(f"gaussianBlur::::54> {blur_value}","0")
        img = cv2.GaussianBlur(img, (blur_value, blur_value),cv2.BORDER_DEFAULT)
        return img

    def grayscale(self,img):
        logger.log(f"grayscale::::59","0")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def resizing(self,img,scale_percent):
        logger.log(f"resizing::::64> {scale_percent}","0")
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)
        return img

    def thresholding(self,img,thresholding_value):
        logger.log(f"thresholding::::72> {thresholding_value}","0")
        mean_value = img.mean()
        threshold_value = mean_value * thresholding_value
        _, img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
        return img

    def OpenAIDataExtract(self,file_path : str, jsonData : str, templates : str):
        # Called when you upload document in import order 
        try:
            
            ent_code = ""
            ent_name = ""
            mandatory = []
            enhancement_parameters = ""
            # enhancement_parameters =    {   
            #     '1': {'Blur': 3},
            #     '2': {'Gray': 1},
            #     '3': {'Resizing': 84},
            #     '4': {'Thresholding': 0.9}
            #                             }
            postOrderExtraction = ""
            proc_mtd_value      = ""
            proc_api_key        = ""
            ai_proc_templ       = ""
            ai_proc_variables   = ""
            input_module        = ""

            logger.log(f"json data   ::::: 61 {jsonData}","0")
            logger.log(f"OpenAIDataExtract all Parameters::  \n{locals()}\n","0")
            
            if 'ai_proc_templ' in jsonData.keys():
                ai_proc_templ = jsonData['ai_proc_templ']
            
            if 'proc_api_key' in jsonData.keys():
                proc_api_key = jsonData['proc_api_key']

            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId']
                
            if 'objName' in jsonData.keys():
                objName = jsonData['objName']

            if 'ent_code' in jsonData.keys():
                ent_code = jsonData['ent_code']

            if 'ent_name' in jsonData.keys():
                ent_name = jsonData['ent_name']
 
            if 'IS_OCR_EXIST' in jsonData.keys():
                IS_OCR_EXIST = jsonData['IS_OCR_EXIST']

            if 'ai_proc_variables' in jsonData.keys():
                ai_proc_variables = jsonData['ai_proc_variables']

            if 'enhancement_parameters' in jsonData.keys():
                enhancement_parameters = jsonData['enhancement_parameters']
                if enhancement_parameters:
                    enhancement_parameters = json.loads(enhancement_parameters)

            if isinstance(ai_proc_variables, str):
                ai_proc_variables = json.loads(ai_proc_variables)

            if ai_proc_variables:
                for val in ai_proc_variables["Details"]:
                    if val['mandatory'] == 'true':
                        mandatory.append(val['name'])
                
                    if val["name"] == "POST_ORDER_EXTRACTION":
                        postOrderExtraction = val['defaultValue'].strip()
                        logger.log(f"\n\n POST_ORDER_EXTRACTION ::: {postOrderExtraction} {type(postOrderExtraction)}\n\n","0") 
        
                
            logger.log(f"ai_proc_variables::::88> {ai_proc_variables}","0")
            
            if 'proc_mtd' in jsonData.keys():
                proc_mtd = jsonData['proc_mtd']
                proc_mtd_value = proc_mtd.split("-")
                logger.log(f"proc_mtd_value:::{proc_mtd_value}")
            
            self.processing_method = proc_mtd_value[0]
            logger.log(f"self.processing_method ::: {self.processing_method}")
           
            OCR_Text = ""
            finalResult = ""
            self.result = {}
            df = None
            fileExtension = (pathlib.Path(file_path).suffix)
            logger.log(f"\nfileExtention::::> {fileExtension}","0")
            self.fileExtension_lower = fileExtension.lower()
            logger.log(f"\nfileExtention_lower()::::> {self.fileExtension_lower}","0")

            if IS_OCR_EXIST == 'false':
                logger.log(f"OCR Start !!!!!!!!!!!!!!!!!102","0")  
                dict = {}          
                if '.PDF' in self.fileExtension_lower or '.pdf' in self.fileExtension_lower or '.png' in self.fileExtension_lower :

                    if 'PP' == proc_mtd_value[0] :
                        OCR_Text=self.pdfplumber_ocr(file_path)
                        from invoice2data.input import pdftotext
                        input_module = pdftotext
                        logger.log(f"\nLoading 'pdftotext' module for case 'PP'\n ")

                    elif 'PT' == proc_mtd_value[0]:
                        OCR_Text=self.pdftotext_ocr(file_path)
                        from invoice2data.input import pdftotext
                        input_module = pdftotext
                        logger.log(f"\nLoading 'pdftotext' module for case 'PT'\n")

                    elif 'PO' == proc_mtd_value[0]:
                        OCR_Text, file_path =self.pytesseract_ocr(file_path)
                        logger.log(f"\nLoading 'tesseract' module for case 'PO'\n ")
                        from invoice2data.input import tesseract
                        input_module =  tesseract
                    
                    elif 'PPO' == proc_mtd_value[0] or 'PPO4' == proc_mtd_value[0] :
                        logger.log("\tCASE PPO OR PPO4\n")
                        OCR_Text=self.pdfplumber_overlap(file_path)

                        from invoice2data.input import pdftotext
                        input_module = pdftotext
                        logger.log(f"\nLoading 'pdftotext' module for case 'PPO' OR 'PPO4'\n ")

                    elif 'PPF' == proc_mtd_value[0]:
                        logger.log("\tCASE PPF\n")
                        OCR_Text=self.PyPDF_ocr(file_path)
                        logger.log(f"\nLoading 'tesseract' module for case 'PPF'\n ")
                        from invoice2data.input import tesseract
                        input_module =  tesseract 
                        
                    elif 'PPH' == proc_mtd_value[0]:
                        logger.log("\nCASE PPH\n")
                        finalResult=self.process_image(file_path,proc_api_key,ai_proc_templ, ai_proc_variables)
                        logger.log(f"finalResult : {finalResult}")

                    # if len((OCR_Text).strip()) == 0: 
                    if 'PPH' != proc_mtd_value[0]:
                        keys_with_blank_values = [key for key, value in OCR_Text.items() if not value]
                        if len(keys_with_blank_values) != 0:      
                            OCR_Text, file_path =self.pytesseract_ocr(file_path)
                            
                            logger.log(f"\nLoading 'tesseract' module since IMAGE is found in file.\n ")
                            from invoice2data.input import tesseract
                            input_module =  tesseract 

                    logger.log(f"OpenAI pdf ocr ::::: {OCR_Text}","0")
                
                elif '.docx' in self.fileExtension_lower or '.DOCX' in self.fileExtension_lower:
                    dict[str(1)] = docx2txt.process(file_path)
                    OCR_Text = dict
                    logger.log(f"OpenAI DOCX ocr ::::: {OCR_Text}","0")

                # Added by SwapnilB for handling xls case on 28-Mar-23 [START]
                elif ".xls" in self.fileExtension_lower or ".xlsx" in self.fileExtension_lower:
                    logger.log(f"inside .xls condition","0")
                    df = pd.read_excel(file_path)
                    xls_ocr = df.to_csv()
                    dict[str(1)] = xls_ocr.replace(","," ").strip()
                    OCR_Text = dict
                    logger.log(f"\nxls_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\nxls_ocr ::::: \n{OCR_Text}\n","0")
                    
                elif ".csv" == self.fileExtension_lower :
                    logger.log(f"inside .csv condition","0")
                    df = pd.read_csv(file_path)
                    csv_ocr = df.to_csv()           # to handle multiple spaces between columns
                    dict[str(1)] = csv_ocr.replace(","," ")
                    OCR_Text = dict
                    logger.log(f"\ncsv_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\ncsv_ocr ::::: \n{OCR_Text}\n","0")
                
                elif ".rtf" == self.fileExtension_lower :
                    logger.log(f"inside .rtf condition","0")
                    with open(file_path) as infile:
                        content = infile.read()
                        dict[str(1)] = rtf_to_text(content, errors="ignore")  # to handle encoding error
                    OCR_Text = dict
                    logger.log(f"\nrtf_ocr type ::::: \t{type(OCR_Text)}","0")
                    logger.log(f"\nrtf_ocr ::::: \n{OCR_Text}\n","0")
                
                # Added by SwapnilB for handling xls case on 28-Mar-23 [END]

                else:
                    path = file_path
                    image = cv2.imread(path)
                    if enhancement_parameters:
                        if '1' in enhancement_parameters.keys():
                            image = self.gaussianBlur(image,enhancement_parameters['1']['Blur'])
                        
                        if '2' in enhancement_parameters.keys():
                            image = self.grayscale(image)

                        if '3' in enhancement_parameters.keys():
                            image = self.resizing(image,enhancement_parameters['3']['Resizing'])
                        
                        if '4' in enhancement_parameters.keys():
                            image = self.thresholding(image,enhancement_parameters['4']['Thresholding'])


                    dict[str(1)] = pytesseract.image_to_string(image)
                    logger.log(f"\nImage inside pdf CASE\n","0")
                    logger.log(f"\nOCR ::: {dict}\n","0")
                    OCR_Text = dict

                    if len(OCR_Text) > 0:
                        logger.log("\n else 299 \n")
                        self.textFile_Path = file_path[:-3] + "txt"
                        with open(self.textFile_Path ,"w") as txt_fileObj :
                            txt_fileObj.write("\n".join(OCR_Text.values()))
                            logger.log(f"\nfileObj::: {txt_fileObj}\n")
                        
                        file_path = self.txt_To_Pdf(self.textFile_Path)
                        
                        logger.log(f"\nLoading 'tesseract' module since IMAGE is found in file.\n")
                        from invoice2data.input import tesseract
                        input_module =  tesseract 

                if 'PPH' != proc_mtd_value[0]:
                        
                    for pageNo in OCR_Text:
                        logger.log(f"\n i value ::: {pageNo }\n")
                        # if pageNo == '1' and len(OCR_Text[pageNo]) == 0 :
                        #         logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
                        #         trace = str('Contact System Administrator')
                        #         descr = str(f' First Page cannot be blank. \n OCR is not available for page {pageNo}')
                        #         returnErr = common.getErrorXml(descr, trace)
                        #         logger.log(f'\n Print exception returnSring insideprocess_image OCR : {returnErr}', "0")
                        #         return str(returnErr)
                        if len(OCR_Text[pageNo]) == 0 :
                            logger.log(f"\nEmpty OCR found for page::: {pageNo} \n") 
                            continue
                        
                logger.log(f"OCR End !!!!!!!!!!!!!!!!!156","0")
                if 'PPH' != proc_mtd_value[0]:
                    if not ent_code and not ent_name:
                        logger.log(f"INSIDE entcode and entname not blank","0")
                        try:                                                        # Load modules for template fetching
                            # if proc_mtd_value[0] == 'PT':
                            #     logger.log(f"Loading 'tesseract' module for case 'PT' ")
                            #     from invoice2data.input import pdftotext
                            #     input_module = pdftotext

                            # elif proc_mtd_value[0] == 'PP'  :
                            #     # from invoice2data.input import pdfplumber
                            #     # input_module = pdfplumber
                            #     logger.log(f" Loading 'pdftotext' for 'PP'","0")
                            #     from invoice2data.input import pdftotext
                            #     input_module = pdftotext
                                
                            # elif proc_mtd_value[0] == 'PO' or proc_mtd_value[0] == 'PPF' or proc_mtd_value[0] == 'PPO' or proc_mtd_value[0] == 'PPO4' :
                            #     logger.log(f"Loading 'tesseract' module for case 'PO' OR 'PPF' OR 'PPO' OR 'PPO4' ")
                            #     from invoice2data.input import tesseract
                            #     input_module =  tesseract

                        
                            logger.log(f"Template Extraction call Start !!!!!!!!!!!!!!!!!183","0")
                            logger.log(f"\n file_path line 346 ::: {file_path} \n input_module ::: {input_module}\n","0")
                            resultdata = extract_data(invoicefile=file_path,templates=templates,input_module=input_module)
                            # resultdata = dict(resultdata)
                            logger.log(f"Template Extraction call End !!!!!!!!!!!!!!!!!111","0")
                            logger.log(f"Template extracted data  ::::: 186 {resultdata}","0")
                            logger.log(f"resultdata type  ::::: 187 {type(resultdata)}","0")
                            
                            if isinstance(resultdata, bool) and len(mandatory)>0:
                                logger.log(f"resultdata type  ::::: 283 {type(OCR_Text)}","0")
                                self.result['OCR_DATA']=OCR_Text
                                self.result['isMandatoryExtracted']='false'
                                return self.result
                                # resultdata = {}
                            elif isinstance(resultdata, bool):
                                resultdata = {}

                            resultdata['isTemplateExtracted']='true'
                            self.result['isMandatoryExtracted']='true'

                            if mandatory:
                                for valuesOfmandatory in mandatory:
                                    if valuesOfmandatory in resultdata:
                                        if not resultdata[valuesOfmandatory]:  
                                            self.result['OCR_DATA']=OCR_Text
                                            self.result["EXTRACT_TEMPLATE_DATA"] = resultdata
                                            self.result['isMandatoryExtracted']='false'
                                            return self.result
                                                                
                            for valuesOfmandatory in resultdata.keys():
                                if type(resultdata[valuesOfmandatory]) == list and resultdata[valuesOfmandatory] != []:
                                    resultdata[valuesOfmandatory] = resultdata[valuesOfmandatory][0]
                                elif resultdata[valuesOfmandatory] == []:
                                    resultdata[valuesOfmandatory] = ""

                            # resultdata['isTemplateExtracted']='true'
                            if 'ent_code' in resultdata.keys():
                                self.result["EXTRACT_TEMPLATE_DATA"] = resultdata
                                self.result['OCR_DATA']=OCR_Text
                                return self.result
                                
                            
                        except Exception as e:
                            logger.log(f'\n Exception : {e}', "1")

            else:
                if 'OCR_DATA' in jsonData.keys():
                    OCR_Text = jsonData['OCR_DATA']

            if len(postOrderExtraction) > 0 :
                    OCR_Text = self.replace_OCR_Word(OCR_Text, postOrderExtraction )
                    logger.log(f"After POST-Order-Extraction OCR_Text::: \t{type(OCR_Text)} \n{OCR_Text}\n")

            if ai_proc_templ:
                if 'PPH' != proc_mtd_value[0]: 
                    if 'AID' in proc_mtd_value[1]:
                        logger.log(f"AID !!!!!!!!!!!! 204","0")
                        finalResult = self.extractdatausing_davinci(proc_api_key=proc_api_key, OCR_Text=OCR_Text, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables)
                
                    elif 'AIT' in proc_mtd_value[1]:
                        finalResult = self.extractdatausing_turbo(proc_api_key = proc_api_key, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables, OCR_Text = OCR_Text,userId = self.userId)
                
                self.result["EXTRACT_LAYOUT_DATA"] = finalResult
                self.result['OCR_DATA']=OCR_Text
            
            logger.log(f"Response Return !!!!!!!!!!!! 142","0")
            return self.result
            
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)


    def getlayouttextaidata(self):
        # Called when you click 'REFRESH' upload document in import order 
        try:
            result = {}
            final_result = {}
            mandatory = []
            finalResult = ""
            proc_api_key = ""
            ai_proc_templ = ""
            ent_name = ""
            ent_code = ""
            ent_type = ""
            OCR_Text = ""
            ai_proc_variables   = ""
            postOrderExtraction = ""
            proc_mtd_value = ""
            
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"jsonData API openAI class::: !!!!!269 {jsonData}","0")

            if 'extract_templ' in jsonData.keys():
                given_temp_path = jsonData['extract_templ']
            
            if 'ent_code' in jsonData.keys():
                ent_code = jsonData['ent_code']
            
            if 'ent_type' in jsonData.keys():
                ent_type = jsonData['ent_type']

            if 'ent_name' in jsonData.keys():
                ent_name = jsonData['ent_name']

            if 'ai_proc_templ' in jsonData.keys():
                ai_proc_templ = jsonData['ai_proc_templ']

            if 'ai_proc_variables' in jsonData.keys():
                ai_proc_variables = jsonData['ai_proc_variables']

            if 'proc_api_key' in jsonData.keys():
                proc_api_key   = jsonData['proc_api_key']

            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId']

            if 'objName' in jsonData.keys():
                objName = jsonData['objName']
            
            if 'proc_mtd' in jsonData.keys():
                proc_mtd = jsonData['proc_mtd']
                proc_mtd_value = proc_mtd.split("-")
            
            if 'OCR_DATA' in jsonData.keys():
                OCR_Text = jsonData['OCR_DATA']
            logger.log(f'\n\n  OCR_Text line 406: \n{OCR_Text}\n{type({OCR_Text})}\n{len({OCR_Text})}\n', "0")
            
            self.processing_method = proc_mtd_value[0]
            logger.log(f"self.processing_method ::: {self.processing_method}")

            if ai_proc_variables:
                for val in ai_proc_variables["Details"]:
                    if val["name"] == "POST_ORDER_EXTRACTION":
                        postOrderExtraction = val['defaultValue'].strip()
                        logger.log(f"\n\n POST_ORDER_EXTRACTION ::: {postOrderExtraction} {type(postOrderExtraction)}\n\n","0") 

            if len(postOrderExtraction) > 0 :
                logger.log(f'\n\n  Inside line 424 \n', "0")
                OCR_Text = json.dumps(self.replace_OCR_Word(OCR_Text, postOrderExtraction))
                logger.log(f'\n\n   \n{type({OCR_Text})}\n{OCR_Text}') #\n{len({OCR_Text})}\n', "0")

            if ai_proc_templ:
                ymlfilepath = "/"+(given_temp_path)+"/"+str(ent_name).strip().replace(" ","_").replace(".","").replace("/","")+".yml"
                if os.path.exists(ymlfilepath) == True:
                    os.remove(ymlfilepath)
                logger.log(f'\n\n  OCR_Text line 431: \n') 
            
                if ent_name.strip() and ((isinstance(ent_code, str) and ent_code.strip()) or isinstance(ent_code, int)):  
                    logger.log(f"ent_name :::\t{type(ent_name)}{ent_name} \n ent_code :::\t{type(ent_code)}{ent_code} \n OCR_Text:::{type(OCR_Text)}\n {OCR_Text}" )
                    if ent_name in OCR_Text:
                        logger.log(f'\n[ Template creation Start time  305  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                        templatecreation = GenerateExtractTemplate()
                        templatecreation.generateHeaderTemplate(ymlfilepath,ent_name,ent_code,ent_type,ai_proc_variables,OCR_Text)
                        logger.log(f'\n[ Template creation End time  308  :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                    else:
                        message = str('Template not created, Please enter valid Received From Name')
                        description = str('Received From Name must be present in file')
                        errorjson = common.getErrorJson(message,description)
                        final_result['status'] = 0
                        final_result['error'] = errorjson
                        return final_result
                
                temp_file_path = "/"+(given_temp_path)+"/"+'.yml'
                if os.path.exists(temp_file_path) == True:
                    os.remove(temp_file_path)
                    message = str('Template not created')
                    description = str('Ent Code or Ent Name is not present, mention required details properly')
                    errorjson = common.getErrorJson(message,description)
                    final_result['status'] = 0
                    final_result['error'] = errorjson
                    logger.log(f'\n[ Blank Template Remove :          {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
                    return final_result
                
                if 'AID' in proc_mtd_value[1]:
                    finalResult = self.extractdatausing_davinci(proc_api_key=proc_api_key, OCR_Text=OCR_Text, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables)

                elif 'AIT' in proc_mtd_value[1]:
                    finalResult = self.extractdatausing_turbo(proc_api_key = proc_api_key, ai_proc_templ=ai_proc_templ,ai_proc_variables=ai_proc_variables, OCR_Text = OCR_Text,userId = self.userId)
                
                if os.path.exists(ymlfilepath) == True:
                    result["EXTRACT_LAYOUT_DATA"] = finalResult
                    final_result['status'] = 1
                    final_result['result'] = result
                else:
                    message = str('Template not created, Mention the Required details properly')
                    description = str('Recieved From Name and Recieved From Code always requird')
                    errorjson = common.getErrorJson(message,description)
                    final_result['status'] = 0
                    final_result['error'] = errorjson

        except Exception as ex:
            final_result['status'] = 0
            final_result['error'] = str(ex)
            logger.log(f"Return result value !!!!!!!!! 203 {final_result}","0")
            trace = traceback.format_exc()
            descr = str(ex)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
        
        return final_result
    
    def extractdatausing_davinci(self,proc_api_key : str, OCR_Text : str , ai_proc_templ : str, ai_proc_variables : str):

        logger.log(f'\n[ Open ai starting time 131 :        {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
        openai.api_key = proc_api_key
        logger.log(f"\nai_proc_variables::::\n {ai_proc_variables}\n{type(ai_proc_variables)}","0")
        logger.log(f"\nai_proc_templ::::\n {ai_proc_templ}\n{type(ai_proc_templ)}","0")       
        logger.log(f"TYPE OF ai_proc_variables {type(ai_proc_variables)}","0")

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)

        if ai_proc_variables:
            for val in ai_proc_variables["Details"]:
                if "<"+val["name"]+">" in ai_proc_templ:
                    ai_proc_templ = ai_proc_templ.replace("<"+val["name"]+">", val['defaultValue'])

        if '<DOCUMENT_DATA>' in ai_proc_templ:
            print(type(ai_proc_templ))
            ai_proc_templ = ai_proc_templ.replace('<DOCUMENT_DATA>',OCR_Text)
            logger.log(f'\n[ Open ai " model " Value              :      "text-davinci-003" ]', "0")
            logger.log(f'\n[ Open ai " prompt " Value             :      "{ai_proc_templ}" ]', "0")
            logger.log(f'\n[ Open ai " temperature " Value        :      "0" ]', "0")
            logger.log(f'\n[ Open ai " max_tokens " Value         :      "1800" ]', "0")
            logger.log(f'\n[ Open ai " top_p " Value              :      "1" ]', "0")
            logger.log(f'\n[ Open ai " frequency_penalty " Value  :      "0" ]', "0")
            logger.log(f'\n[ Open ai " presence_penalty " Value   :      "0" ]', "0")
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt= ai_proc_templ,
            temperature=0,
            max_tokens=1800,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

        else:

            logger.log(f'\n[ Open ai " model " Value              :      "text-davinci-003" ]', "0")
            logger.log(f'\n[ Open ai " prompt " Value             :      "{OCR_Text+ai_proc_templ}" ]', "0")
            logger.log(f'\n[ Open ai " temperature " Value        :      "0" ]', "0")
            logger.log(f'\n[ Open ai " max_tokens " Value         :      "1800" ]', "0")
            logger.log(f'\n[ Open ai " top_p " Value              :      "1" ]', "0")
            logger.log(f'\n[ Open ai " frequency_penalty " Value  :      "0" ]', "0")
            logger.log(f'\n[ Open ai " presence_penalty " Value   :      "0" ]', "0")
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt= OCR_Text+'\n'+ai_proc_templ,
            temperature=0,
            max_tokens=1800,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        logger.log(f"Response openAI completion endpoint::::: {response}","0")
        finalResult=str(response["choices"][0]["text"])
        logger.log(f'\n [ Open ai completion time 171 :      {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', "0")
        logger.log(f"OpenAI completion endpoint finalResult ::::: {finalResult}","0")
        return finalResult


    def extractdatausing_turbo(self,proc_api_key: str, ai_proc_templ : str, ai_proc_variables : str, OCR_Text : str,userId : str):
        logger.log(f"\nai_proc_variables::::\n {ai_proc_variables}\n{type(ai_proc_variables)}","0")
        logger.log(f"\nai_proc_templ::::\n {ai_proc_templ}\n{type(ai_proc_templ)}","0")
        logger.log(f"\nai_OCR_Text::::  512\n {OCR_Text}\n{type(OCR_Text)}","0")
        OCR_List            = []
        response_lst        = []
        start               = "" 
        end                 = ""
        ext_min_len         = ""
        FinalsubString_OCR  = ""
        page_wise           = "Yes"
        
        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)
        
        if isinstance(OCR_Text, str):
            OCR_Text = json.loads(OCR_Text.strip())
        
        if isinstance(OCR_Text, dict):
            for val in OCR_Text.values():
                OCR_List.append(val)
            OCR_Text = OCR_List


        if isinstance(ai_proc_templ, list):
            ai_proc_templ = json.dumps(ai_proc_templ)

        if ai_proc_variables:
            for val in ai_proc_variables["Details"]:
                if "<"+val["name"]+">" in ai_proc_templ:
                    ai_proc_templ = ai_proc_templ.replace("<"+val["name"]+">", val['defaultValue'].strip())

                if val["name"] == "start_index":
                    start = val['defaultValue'].strip()
                    logger.log(f"\n\n start_index ::: {start} \n\n","0")    

                if val["name"] == "end_index":
                    end = val['defaultValue'].strip()
                    logger.log(f"\n\n end_index ::: {end} \n\n","0") 
                
                if val["name"] == "ext_min_len":
                    ext_min_len = val['defaultValue'].strip()
                    logger.log(f"\n\n ext_min_len ::: {ext_min_len} {type(ext_min_len)}\n\n","0") 
                
                if val["name"] == "ext_pagewise":
                    page_wise = val['defaultValue'].strip()
                    logger.log(f"\n\n page_wise ::: {page_wise} {type(page_wise)}\n\n","0") 

        start_lst = start.split(",")
        end_lst = end.split(",")
        subStringOcrList = []
        
        if page_wise == "No" or self.fileExtension_lower == 'csv' or self.fileExtension_lower == 'xls' or self.fileExtension_lower == 'xlsx':
            joined_OCR_List =  []
            logger.log(f"\n\n inside 'page_wise = No' condition:::{OCR_Text} \n\n","0")
            logger.log(f"\n\n before OCR_Text:::{OCR_Text} \t{type(OCR_Text)} \n\n","0")
            joined_OCR_List.append("\n".join(OCR_Text))
            logger.log(f"\n\n after joined_OCR_List:::{joined_OCR_List} \t{type(joined_OCR_List)} \n\n","0")
            OCR_Text_withInstruction = self.replaceWithExtractInstruction(ai_proc_temp=ai_proc_templ, OCR_Text = joined_OCR_List, ai_proc_variables = ai_proc_variables, page_wise = page_wise )
            logger.log(f"\n\n after OCR_Text_withInstruction:::{OCR_Text_withInstruction} \t{type(OCR_Text_withInstruction)} \n\n","0")
            openAIResponseStr = self.call_GPT_Service(OCR_Text_withInstruction, proc_api_key,userId)
            response_lst.append(openAIResponseStr)
            finalResponseStr = self.concatFinalResponse(returnedResponseList = response_lst)
            logger.log(f"OpenAI FINAL ResponseStr  :::\n\n{finalResponseStr}\n\n","0")  
        
            return finalResponseStr

        else:
            # create substring 
            for page in range(len(OCR_Text)):
                FinalsubString_OCR = ""
                startIndex         = ""
                endIndex           = ""
                
                for start_word in start_lst:
                    if start_word != "" and OCR_Text[page].find(start_word) != -1:
                        logger.log(f"inside if start loop", "0")
                        startIndex = OCR_Text[page].find(start_word)
                        logger.log(f"startIndex value::{startIndex}","0")# \t {page}")
                    break

                for end_word in end_lst:
                    if end_word != "" and OCR_Text[page].find(end_word) != -1:
                        logger.log(f"inside if end loop", "0")
                        endIndex = OCR_Text[page].find(end_word)
                        logger.log(f"endIndex value::{endIndex}  \t {page}\n\n", "0")
                    break
                
                if (startIndex != -1 and startIndex != "") and (endIndex != -1 and endIndex != ""):
                    logger.log(f"\n\nstartIndex and endIndex not blank case\n", "0")
                    FinalsubString_OCR = OCR_Text[page][ startIndex : endIndex ]

                    if isinstance(ext_min_len, str) and len(ext_min_len) > 0:
                        if len(FinalsubString_OCR) > int(ext_min_len) :
                            logger.log(f"\n\n FinalsubString_OCR length: {len(FinalsubString_OCR)} is GREATER THAN Ext_min_len: {ext_min_len} for Page: {page} condition.   \n\n","0")
                            subStringOcrList.append(FinalsubString_OCR)
                        else:
                            logger.log(f"\n\n Ext_min_len {ext_min_len} is GREATER THAN FinalsubString_OCR length {len(FinalsubString_OCR)} for Page: {page} condition. \n\n","0")
                    
                elif (startIndex != -1 and startIndex != "") and (endIndex == -1 or endIndex == ""):
                    logger.log("\n\nEndIndex blank case\n ","0")
                    FinalsubString_OCR = OCR_Text[page][ startIndex :  ]
        
                elif (startIndex == -1 or startIndex == "") and (endIndex != -1 and endIndex != ""):
                    FinalsubString_OCR = OCR_Text[page][ : endIndex ]
                    logger.log(f"\n\nStartIndex empty case\n", "0")
                    
                elif (startIndex == -1 or startIndex == "") and (endIndex == -1 or endIndex == ""):
                    logger.log(f"\n\nStartIndex EndIndex empty case\n", "0")
                    FinalsubString_OCR = OCR_Text[page]
                    
                else:
                    FinalsubString_OCR = OCR_Text[page]
                
                logger.log(f"FinalsubString_OCR :::{FinalsubString_OCR}", "0")
                if FinalsubString_OCR != "" :
                    subStringOcrList.append(FinalsubString_OCR)
                else:
                    logger.log(f"FinalsubString_OCR 'else' line 639:::{FinalsubString_OCR}", "0")

            if len(subStringOcrList) > 0:
                logger.log(f"\n\n if condition line FINAL subStringOcrList::{subStringOcrList} length :::{len(subStringOcrList)}\n\n","0")
                OCR_Text =  subStringOcrList
            else:
                message ="There is no OCR text found against the given extraction details."
                logger.log(f"\n\n Line 584 ext_min greater than OCR length\n\n","0")
                return message

        ai_proc_templ_updated = self.replaceWithExtractInstruction(ai_proc_temp=ai_proc_templ, OCR_Text = OCR_Text, ai_proc_variables = ai_proc_variables, page_wise = page_wise )
        
        # Overview call or Template creation call ai_proc_templ variable type is list and while uploading it's variable type is string
        if isinstance(ai_proc_templ_updated, str):       
            # ai_proc_templ_updated = ai_proc_templ_updated #10-aug-23 .replace('\n'," ") 
            ai_proc_templ_updated = json.loads(ai_proc_templ_updated)
        
        logger.log(f"\n\nai_proc_templ_updated     ::: {type(ai_proc_templ_updated)} \t {len(ai_proc_templ_updated)}\n\n","0")

        for i in range(len(ai_proc_templ_updated)):
            logger.log(f"\n\n inside 'page_wise = Yes' condition for page: {i}\n\n","0")
            openAI_result = self.call_GPT_Service(ai_proc_templ_updated[i], proc_api_key, userId)
            response_lst.append(openAI_result)
        
        logger.log(f"OpenAI response_lst  :::\n\n{response_lst}\n\n","0")  
        finalResponseStr = self.concatFinalResponse(returnedResponseList = response_lst)
        logger.log(f"\n\nAll Pages FinalResponseString ::: \n{finalResponseStr}\n\n")
        
        return finalResponseStr

    def replaceWithExtractInstruction(self, ai_proc_temp: str, OCR_Text: list, ai_proc_variables : str, page_wise : str):
        logger.log(f"\n\niNSIDE replaceWithExtractInstruction()\n\n","0")
        logger.log(f"\n\nOCR_Text line 637::::{OCR_Text}{type(OCR_Text)}\n\n","0")
        logger.log(f"\n\nai_proc_temp::::{ai_proc_temp}{type(ai_proc_temp)}\n\n","0")
        replacedOCR_MainPage  = ""
        replacedOCR_OtherPage = ""

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)

        for key in ai_proc_variables["Details"]:
            if key["name"] == "main_page":
                self.mainPg_Instruction = key['defaultValue']
        logger.log(f"mainPg_Instruction:::\n\n{self.mainPg_Instruction}\n","0")

        for key in ai_proc_variables["Details"]:
            if key["name"] == "other_pages":
                self.otherPg_Instruction = key['defaultValue']
        logger.log(f"otherPg_Instruction:::\n\n{self.otherPg_Instruction}\n","0")
        
        FinalInstruction_lst = []
        replacedOCR_MainPage = OCR_Text[0].replace('"',' ').replace("\\n", " ").replace("\n", " ") # 10-aug-23  .replace("\\",'\/')
        ai_proc_temp_main = (ai_proc_temp.replace("<EXTRACT_INSTRUCTIONS>", self.mainPg_Instruction)).replace("<DOCUMENT_DATA>", replacedOCR_MainPage) # 10-aug-23.replace('"',' ').replace("\\",'\/')).strip()
        logger.log(f"\n\ai_proc_temp_main::::{ai_proc_temp_main}{type(ai_proc_temp_main)}\n\n","0")
        if page_wise == "No": 
            return ai_proc_temp_main
        else:
            FinalInstruction_lst.append(ai_proc_temp_main)
        # other Page OCR

        if len(OCR_Text) > 1:
            for i in range(1, len(OCR_Text)):
                replacedOCR_OtherPage = OCR_Text[i].replace('"',' ').replace("\\n", " ").replace("\n", " ")  # 10-aug-23 .replace("\\",'\/')
                ai_proc_temp_other = (ai_proc_temp.replace("<EXTRACT_INSTRUCTIONS>", self.otherPg_Instruction)).replace("<DOCUMENT_DATA>", replacedOCR_OtherPage)  # 10-aug-23.replace('"',' ').replace("\\",'\/')).strip()
                FinalInstruction_lst.append(ai_proc_temp_other)
        logger.log(f"\n\FinalInstruction_lst line 647::::{FinalInstruction_lst}\t {type(FinalInstruction_lst)}\n\n","0")
        return FinalInstruction_lst

    def concatFinalResponse(self, returnedResponseList : list):
        finalResponse   = []
        pageCSV         = ""
        for i in range(len(returnedResponseList)):
            if i == 0:
                returnedResponseList[i] = returnedResponseList[i].replace("\n```", "").replace("```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","")
                finalResponse.append(returnedResponseList[i])
            else:
                returnedResponseList[i] = returnedResponseList[i].replace("\n```", "").replace("```", "").replace("json","").replace("JSON","").replace("csv","").replace("CSV","")
                fromSizeVar = returnedResponseList[i]
                if "Size" in fromSizeVar:
                    pageCSV = fromSizeVar[fromSizeVar.find("Size")+5:]
                
                elif "Quantity" in fromSizeVar:
                    pageCSV = fromSizeVar[fromSizeVar.find("Quantity")+9:]

                pageCSV = "\n" + pageCSV if not pageCSV.startswith("\n") else pageCSV
                finalResponse.append(pageCSV)
                
        return (" ".join(finalResponse))        

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
    
        return num_tokens

    def call_GPT_Service(self, text, proc_api_key, userId, token_limit = 4096, max_response_tokens = 1800):
        messageTokenLength = None
        openai.api_key = proc_api_key
        completion  = ""
        result      = ""
        
        #to handle any unicode character
        # clean_string = ''.join(c for c in text if unicodedata.category(c)[0] != 'C')   # 10-aug-23 -- commented because '\n' is considered as control character and it was geeting removed
        
        # message = json.loads(text, strict=False)   #(clean_string.replace("\\",'\/'))
        
        message = ast.literal_eval(text)  # to handle escape characters 
        logger.log(f" \n\nBefore GPT CALL FINAL MESSAGE  :::\n{message}, \t{type(message)}","0")    

        # to calculate token
        conv_history_tokens = self.num_tokens_from_messages(message)   
        logger.log(f"conversion_tokens_count:::{conv_history_tokens}","0")    
        messageTokenLength = conv_history_tokens + max_response_tokens 
        logger.log(f"\n\n MessageTokenLength is :::{messageTokenLength}\n","0")
        logger.log(f"\n\n self.processing_method :::{self.processing_method}\n","0")
        
        logger.log("\n\n\nEND\n\n\n")

        logger.log(f'\n  Requesting GPT Service Start Time : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        if self.processing_method == "PPF" or self.processing_method == 'PPO4':
            logger.log(f"\n\n--- Using gpt-4-1106-preview Model ---\t  MessageTokenLength is :::{messageTokenLength}\n","0")
            completion = openai.ChatCompletion.create(
                            model="gpt-4-1106-preview",
                            messages=message,
                            temperature=0,
                            max_tokens=4096,               # Added on 27-Dec-23 because response was returning partial in some cases,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0,
                            user=userId,
                        )
            result = (completion['choices'][0]['message']['content'])
            logger.log(f"\n\n Completion result gpt-4-1106-preview :::\n{result} \t{type(result)}\n","0")
                   
        else:

            if messageTokenLength <= token_limit:
                logger.log(f"\n\n--- Using GPT-3.5-TURBO Model ---\t as messageTokenLength is :::{messageTokenLength}\n","0")
                completion = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=message,
                                temperature=0,
                                max_tokens=max_response_tokens,
                                top_p=1,
                                frequency_penalty=0,
                                presence_penalty=0,
                                user=userId,
                            )
                
                result = (completion['choices'][0]['message']['content'])
                logger.log(f"\n\n Completion result 3.5 :::\n{result} \t{type(result)}\n","0")
                
            
            else:
                logger.log(f"\n\n--- Using GPT-3.5-turbo-16k Model ---\t  as messageTokenLength is:::{messageTokenLength} \n\n","0")
                completion = openai.ChatCompletion.create(
                            # model="gpt-4",
                            model = "gpt-3.5-turbo-16k",
                            messages=message,
                            temperature=0,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0,
                            user=userId,
                                    )
                
                result = (completion['choices'][0]['message']['content'])
                logger.log(f"\n\n Completion result 3.5-turbo-16k :::\n{result} \t{type(result)}\n","0")
        
        logger.log(f'\n  Requesting GPT Service End Time  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        return result

    def pdfplumber_overlap(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}
        
        pdf = pdfplumber.open(fileName)
        ocr_text = pdf.pages
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text(layout=True, x_tolerance=1)
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()
        
        logger.log(f"OCR_dict after overlap:::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict

    def replace_OCR_Word(self, OCR_Text, postOrderExtraction):
        postOrderExtraction_list  = []
        sourceTarget_mainList     = []
        
        if type(OCR_Text) == str :
            OCR_Text = json.loads(OCR_Text)
            logger.log(f"Before postOrderExtraction OCR_Text::: \t{type(OCR_Text)}\t Length: {len(OCR_Text)} \n{OCR_Text}\n")
            
        if "/n" in postOrderExtraction and "==" in postOrderExtraction:
            postOrderExtraction_list = postOrderExtraction.split("/n")
            logger.log(f"postOrderExtraction_list::: {postOrderExtraction_list}")

            sourceTarget_mainList= [eachElement.split('==') for eachElement in postOrderExtraction_list]
            logger.log(f"sourceTarget_mainList for '/n' CASE ::: {sourceTarget_mainList}")

            for key in OCR_Text:
                if len(sourceTarget_mainList) > 1 :
                    for sourceTarget_list in sourceTarget_mainList:
                        logger.log(f"sourceTarget_list::{sourceTarget_list}")
                        if len(sourceTarget_list[0].strip()) > 0 and sourceTarget_list[0] in OCR_Text[key]:
                            OCR_Text[key] = OCR_Text[key].replace(sourceTarget_list[0], sourceTarget_list[1])
                            logger.log(f" '{sourceTarget_list[0]}' replaced with '{sourceTarget_list[1]}' in page '{key}. '")
                        else:
                            logger.log(f" {sourceTarget_list[0]} must be blank or not found in page '{key}'")

        elif "/n" not in postOrderExtraction and "==" in postOrderExtraction:
            logger.log(f" \n\n Separation character  '=='  found in postOrderExtraction CASE  \n\n")
    
            sourceTarget_mainList= postOrderExtraction.split('==')
            logger.log(f"sourceTarget_mainList ::: {sourceTarget_mainList}")

            for key in OCR_Text:
                if len(sourceTarget_mainList[0].strip()) > 0  and sourceTarget_mainList[0] in OCR_Text[key]:
                    OCR_Text[key] = OCR_Text[key].replace(sourceTarget_mainList[0], sourceTarget_mainList[1])
                else:
                    logger.log(f" {sourceTarget_mainList[0]} must be blank or not found in page '{key}'")

        else:
            logger.log(f" \n\n Separation characters  '\\n'  and '==' not found in postOrderExtraction CASE  \n\n")
        
        logger.log(f"\n\nAfter postOrderExtraction FINAL OCR_Text::: \t{type(OCR_Text)}\t Length: {len(OCR_Text)} \n{OCR_Text}\n")
        
        return OCR_Text
            
    def PyPDF_ocr(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}

        pdfFileObj = open(fileName, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        ocr_text = pdfReader.pages
        
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()

        logger.log(f"OCR_dict PyPDF :::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict
    
    def process_image(self, filename, api_key, ai_proc_templ, ai_proc_variables):
        logger.log(f"inside process_image {locals()}")
        PPH_Result      = []
        base64_image    = ""
        
        logger.log(f"\nfileExtention_lower()::::> {self.fileExtension_lower}","0")
        try:
            if self.fileExtension_lower == ".pdf":
                logger.log("pdf case\n\n")
                pdf = PdfReader(open(filename, 'rb'))

                for page_num in range(len(pdf.pages)):
                    logger.log(f"page number ::: {page_num}\n")
                    images = convert_from_path(filename, first_page=page_num+1, last_page=page_num+1 )
                    for idx, img in enumerate(images):
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")                    
                        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        logger.log(f"Image converted to encoded String ") 

                        result = self.request_handwrittenImages_API_Service(api_key, ai_proc_templ, base64_image, ai_proc_variables, page_num)
                        PPH_Result.append(result)
                
            else:
                image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif'] 
                if any(self.fileExtension_lower == ext for ext in image_extensions):
                    
                    logger.log(f"\n\nImage case PPH\n\n")
                    with open(filename, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        logger.log(f"Image converted to encoded String ") 
                    
                    result = self.request_handwrittenImages_API_Service(api_key, ai_proc_templ, base64_image, ai_proc_variables)
                    PPH_Result.append(result)
                    
                else:
                    logger.log("Invalid file format or extension")
            
            logger.log(f"PPH Result final List ::: \n{PPH_Result}\n")
            final_call_PPH_string = self.concatFinalResponse(PPH_Result)
            logger.log(f"final_call_PPH_string::: \t{type(final_call_PPH_string)} \n final_call_PPH_string::: \n{final_call_PPH_string}\n")
            return final_call_PPH_string
        
        except Exception as e:
            logger.log(f"Exception ::: \n {e}\n")
            message = traceback.format_exc()
            description = str(e)
            errorjson = common.getErrorJson(message,description)
            raise Exception(errorjson)

    def request_handwrittenImages_API_Service(self, api_key, ai_proc_templ, base64_image, ai_proc_variables, pageNo=0) :
        ai_proc_templ_replace   =  ""
        ai_proc_templ_json      =  ""
        result                  =  ""
        serverUrl               =  "https://api.openai.com/v1/chat/completions"
        headers                 =  {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        payload                 =  {"model" : "gpt-4-vision-preview", "messages" : [] , "max_tokens" : 1500}
        
        try:

            ai_proc_templ = self.replaceInstruction_handwritten(ai_proc_templ, ai_proc_variables, pageNo)

            ai_proc_templ_replace = ai_proc_templ.replace("<base64_image>", base64_image)
            logger.log(f"\nai_proc_templ replaced with encoded string   \n\n")
            ai_proc_templ_json = json.loads(ai_proc_templ_replace)
            logger.log(f"ai_proc_templ::: \t{type(ai_proc_templ_json)} \n\n")
            payload["messages"].append(ai_proc_templ_json)
            
            logger.log(f'\n [ PPH Request time started :      {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]')
            response = requests.post(serverUrl, headers=headers, json=payload)
            logger.log(f'\n [ PPH Request time ended :        {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]')
            
            result = response.json()['choices'][0]['message']['content']
            logger.log(f"PPH Response::: \n{result}\n\n")
            return result
        
        except Exception as e:
            logger.log(f"Exception ::: \n {e}\n")
            message = traceback.format_exc()
            description = str(response.json())
            errorjson = common.getErrorJson(message,description)
            raise Exception(errorjson)
        
    def replaceInstruction_handwritten(self, ai_proc_templ,  ai_proc_variables, pageNo=0) :
        logger.log(f"inside replaceInstruction_handwritten method parameters ::: {locals()}")

        if isinstance(ai_proc_variables, str):
            ai_proc_variables = json.loads(ai_proc_variables)

        for key in ai_proc_variables["Details"]:
            if key["name"] == "main_page":
                self.mainPg_Instruction = key['defaultValue']
        logger.log(f" Handwritten mainPg_Instruction:::\n\n{self.mainPg_Instruction}\n","0")

        for key in ai_proc_variables["Details"]:
            if key["name"] == "other_pages":
                self.otherPg_Instruction = key['defaultValue']
        logger.log(f" Handwritten otherPg_Instruction:::\n\n{self.otherPg_Instruction}\n","0")

        if pageNo == 0 :
            ai_proc_templ = (ai_proc_templ.replace("<EXTRACT_INSTRUCTIONS>", self.mainPg_Instruction))
            logger.log(f"\n\nai_proc_temp for main Page::::{ai_proc_templ}{type(ai_proc_templ)}\n\n","0")
        else:
            ai_proc_templ = (ai_proc_templ.replace("<EXTRACT_INSTRUCTIONS>", self.otherPg_Instruction))
            logger.log(f"\n\nai_proc_templ for other Page::::{ai_proc_templ}{type(ai_proc_templ)}\n\n","0")

        return ai_proc_templ

    def txt_To_Pdf(self, file_path):
        # This function converts the txt file object to pdf file.
        logger.log(f"\nFile Name 1090 ::: \n {file_path}\n","0")
        dot_ind          =  file_path.rindex('.')
        only_name        =  file_path[ file_path.rfind("/") : dot_ind ] 
        html_file_name   =  self.file_storage_path + only_name + ".html"
        output_file_name =  self.file_storage_path + only_name + ".pdf"

        logger.log(f"\nFile_path  before conversion to PDF ::: \n  FilePath ::: {file_path}\n{locals()}\n","0")
        with open(file_path , "r",  encoding="utf-8", errors='replace' ) as file:
            logger.log(f"\nApplied UTF-8 encoding \n")
            with open(html_file_name, "w") as output:
                file = file.read()
                file = file.replace("\n", "<br>")
                output.write(file)

        pdfkit.from_file(html_file_name, output_file_name)              # storing .html file content to .pdf file
        try:
            os.remove(file_path)
            file_path = os.path.join(html_file_name)
            os.remove(file_path)
        except Exception as ex:
            trace = traceback.format_exc()
            descr = str(ex)
            returnErr = common.getErrorXml(descr, trace)
            return returnErr

        file_path = os.path.join(self.file_storage_path, output_file_name)
        logger.log(f" \nFilePath after pdf conversion :::  {file_path} \n","0")
        
        return file_path
