
import fitz
from unidecode import unidecode
from unidecode import unidecode
import json
import re
from ..application_logging.logger import App_Logger


class PDFDocument:
    def __init__(self,pdf_path):
        self.pdf_path=pdf_path
        self.doc=fitz.open(pdf_path)
        
        self.logger = App_Logger()
        self.file_object = open("./logs.txt","a+")
    
    def _extract_contents(self):

        self.logger.log(self.file_object,"Starting in _extract_contents method in structured_file_extraction file......")
        contents=[]
        for i in re.sub(r'\d','',self.doc[1].get_text()).split("\n"):
            if i.strip():
                contents.append(i.upper().strip())
        contents.remove("CONTENTS")
        self.logger.log(self.file_object,"Succsessfully executed in _extract_contents method in structured_file_extraction file......")
        return contents

    def extract_headings(self):
        contents= self._extract_contents()
        self.logger.log(self.file_object,"Starting in extract_headings method in structured_file_extraction file......")

        json_data = {}
        sub_json = {}
        main_heading = ""
        text = ""
        current_head=None
        block_dict = {}
        for i in range(2,len(self.doc)):
            blocks=self.doc[i].get_text('dict')
            block_dict[i]=blocks
        for page_num, blocks in block_dict.items():
            sub_head = "Section 1"
            prev = ""
            count = 0
            after_main = False

            for block in blocks['blocks']:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            if  span['size']>40:

                                main_heading += span['text']
                                if main_heading.strip() in contents:
                                    # print(main_heading)
                                    current_head=main_heading
                                    main_heading=""
                                elif main_heading.strip()=="LEAVE POLICY":
                                    main_heading=""
                            elif span['color'] == 90010:
                                    text+="\n"
                                    text+=span['text'].upper()+"\n"
                            else:
                                text+=unidecode(span['text'])
                if current_head in contents:
                    if current_head:
                        if current_head not in json_data:
                            json_data[current_head]=text

                        else:
                            json_data[current_head]+=text
                        text=""
        self.logger.log(self.file_object,"Succsessfully executed in extract_headings method in structured_file_extraction file......")
        return json_data
    def extract_data(self):

        self.logger.log(self.file_object,"Starting in extract_data method in structured_file_extraction file......")
        t=self.extract_headings()
        data=[]
        for i in t.keys():
            sub_json={}
            sub_json_list=[]
            lins= t[i].split("\n")
            sub_json_list.append({"Heading":i})
            for j in range(len(lins)):
                if j==0 and not lins[j].isupper():
                    sub_json_list.append({"para_graph":lins[j]})
                elif lins[j].isupper():
                    key=lins[j]
                    if j+1<len(lins):
                        sub_json_list.append({"Sub_heading":key, "Paragraph":lins[j+1]})

            if sub_json_list:
                data.append(sub_json_list)
        templates={"fileName":"HR_Policy", 
                  "data":data}
        self.logger.log(self.file_object,"Succsessfully executed in extract_data method in structured_file_extraction file......")
        # print(templates)
        return templates


       
# if __name__=="__main__":
#     print("Running data parsing service")
#     PDFDocument('manager handbook policy in legato.pdf').extract_data()

