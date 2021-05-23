from flask import Flask

from flask_restful import Resource, Api, reqparse
import requests
from PIL import Image
import json

import pytesseract
#pytesseract.pytesseract.tesseract_cmd='C:\Program Files\Tesseract-OCR/tesseract.exe'
import sys
from pdf2image import convert_from_path
import os
import shutil
import re


app = Flask(__name__)
api = Api(app)

APP_ROOT = os.path.dirname(sys.argv[0])

if os.path.join(APP_ROOT, "images//"):
    shutil.rmtree(os.path.join(APP_ROOT, "images//"))

target = os.path.join(APP_ROOT, "images//")

token={ 'BP':['BP','Blood Pressure'],
        'Sugar':['Sugar','Random Sugar'],
        'TSH':['TSH','thyroid stimulating hormone','thyroid'],
        'T4':['T4','Thyroxine'],
        'D-Dimer':['DDimer'],
        'CRP':['CRP','c reactive protein'],
        'HB':['HB','Hemoglobin'],
        'HbA1c':['HbA1c','Glycosylated', 'Glycosylated Hemoglobin'],
        'TLC':['TLC','Total leucocyte count','leucocyte count Total','leucocyte','Total Leukocyte Count','Leukocyte','Leukocyte Count Total'],
        'Cholesterol':['Total Cholesterol','Cholesterol','Cholesterol Total'],
        'HDL':['HDL','high density lipoprotein'],
        'LDL':['LDL','low density lipoprotein'],
        'SPO2':['SPO2','Oxygen'],
        'Heart Rate':['Heart Rate','Heart Beat','Pulse Rate'],
        'Respiratory Rate':['Respiratory Rate'],
        'Fasting Sugar':['Fasting glucose','Fasting blood glucose','Fasting Blood Sugar','Fasting Sugar','FBS'],
        'PP Sugar':['Postprandial Blood Sugar','Postprandial Sugar',' Postprandial glucose','PP Sugar','PPBS'],
        'Temperature':['Temperature','Temp'],
        'ESR':['Erythrocyte Sedimentation Rate','ESR'],
        'KFT':['Kidney Function Test','KFT'],
        'LFT':['Liver function test','LFT'],
        'CBC':['complete blood count','CBC'],
        'HRCT Thorax':['High resolution CT scan','High resolution CT','HRCT','Thorax'],
        'ferritin':['ferritin']
           }


class scrape(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize


        parser.add_argument('tokens', required=True)
        parser.add_argument('imageId', required=True)

        args = parser.parse_args()

        os.mkdir(target)
        url = 'https://doctorconsole.healthok.in/viewImage/{}'.format(args['imageId'])

        response = requests.get(url)

        with open(target+'IMG_ID_{}.pdf'.format(args['imageId']), 'wb') as f:
            f.write(response.content)

        f.close()

        PDF_file = target+'IMG_ID_{}.pdf'.format(args['imageId'])

        pages = convert_from_path(PDF_file, dpi=500)

        image_counter = 1


        for page in pages:

            filename = target+'IMG_ID_{}page_'.format(args['imageId'])+str(image_counter)+".jpg"
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1


        filelimit = image_counter-1

        outfile = target+"out_text.txt"

        f = open(outfile, "a")

        for i in range(1, filelimit + 1):
            filename = target+"IMG_ID_{}page_".format(args['imageId'])+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename))))).lower()
            f.write(text)

        f.close()

#----------------------------------------------
        result={}
        p = re.compile('\d+(\.\d+)?')
        with open(target+"out_text.txt",'r') as f:

            lines =f.readlines()

            for line in lines:
                line=line.replace(',','')
                line=line.replace('-','')
                line=line.replace(';','')
                line=line.replace('(','')
                line=line.replace(')','')
                line=line.replace('%','')
                line=line.replace('[','')
                line=line.replace(']','')

                for tkns in token.keys():
                    if tkns.lower() in args['tokens'].lower():
                        for tkn in token[tkns]:

                            if tkn.lower() in line:

                                words=[]
                                for word in line.split():
                                    words.append(word)



                                for word in words:
                                    if p.match(word) :

                                        if tkns not in result.keys() and line.find(tkn.lower()) < line.find(word):

                                            result[tkns]=word




        f.close()
        shutil.rmtree(target)



        return json.dumps(result, indent = 4),200



api.add_resource(scrape,'/scrape')


if __name__ == '__main__':
    app.run()
