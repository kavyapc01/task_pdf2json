
import re
import os
from os.path import join
import json
import argparse
import subprocess
from collections import OrderedDict
import sys

##install PyMuPDF library to use fitz module to extract text from pdf , if not installed
try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'PyMuPDF'])
finally:
    import fitz

##function to extract candidates email
def extract_email_addresses(text):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    emails = r.findall(text)
    if len(emails)>1:
      email = ','.join([str(elem) for elem in emails]) 
    else:
      email = r.search(text).group(0)
    return email

##function to extract candidates name
def extract_name(text):
    name_search = re.search(r"([A-Za-z]+\s+[A-Za-z]+)", text)
    name = name_search.group(0)
    return name

##function to extract candidates address
def extract_address(text):
    xxx = re.search(r'\((.*?)\)+\s+[A-Z-]+',text).group(0)
    citystatecode = re.search(r'[A-Za-z]{4}\,\s+[A-Za-z]{5}\s+[A-Za-z]{3}\s+[A-Za-z]{4}',text).group(0)
    address = xxx + "," +citystatecode
    return address

##function to extract candidates education,professional exp,leadership exp,additional projects,skills & interests
def data_extraction(text_split,dataContent):
    ind = [idx for idx, s in enumerate(text_split) if dataContent in s][0]
    content = text_split[ind]
    contents1 = re.sub(dataContent,'',content)
    contents = re.sub('\s+',' ',contents1)
    return contents

def arg_parser():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('--input', type=str)
    my_parser.add_argument('--output', type=str)
    args = vars(my_parser.parse_args())
    return args

##function to check arguments are correctly passed
def check_args(args):
    n_args = sum([ 1 for a in args.values( ) if a])
    if n_args == 0:
        flag = 2
    elif n_args == 1:
        if args["input"] == None:
            flag = 0
        else:
            flag = 1
    else:
        flag = 3
    return flag 
     


if __name__ == "__main__":
    args = arg_parser()
    flag = check_args(args)
    if flag == 2:
        print("both input and output args are missing")
    elif flag == 0:
        print("input arg is missing")
    elif flag == 1:
        print("output arg is missing")
    else:
        input_file_pdf = str(args['input'])
        output_file_json = str(args['output'])
        
        if not os.path.isfile(input_file_pdf):
            print("File does not exist")
        else:
            df = fitz.open(input_file_pdf)
            text = df.loadPage(0).getText("text")
            text = re.sub(r"[_\u200b]", "", text, flags=re.I)
            text_split = re.split(r'\n(?=Education|Leadership|Professional|Additional|Skills)',text)
            name = extract_name(text)
            email = extract_email_addresses(text)
            address = extract_address(text)
            education = text=data_extraction(text_split,"Education").lstrip()
            prof_exp = data_extraction(text_split,"Professional Experience").lstrip()
            lead_exp = data_extraction(text_split,"Leadership Experience").lstrip()
            add_proj =  data_extraction(text_split,"Additional Projects").lstrip()
            skills_intrst = data_extraction(text_split,"Skills & Interests").lstrip()

            data = OrderedDict([
                ("name",name),
                ("address",address),
                ("email",email),
                ("Education",education),
                ("Professional Experience",prof_exp),
                ("Leadership Experience",lead_exp),
                ("Additional Projects",add_proj),
                ("Skills & Interests",skills_intrst)
                ])

            json_data = json.dumps(data,ensure_ascii=False,sort_keys=False)
            with open(output_file_json, 'w') as json_file:
                json_file.write(json_data)
            print("Data written to %s file" %output_file_json)


