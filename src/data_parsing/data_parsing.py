from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from qdrantdb import QdrantEmbedding
# from application_logging import logger
# from application_logging.logger import App_Logger
# from application_logging.logger import App_Logger
# from ..application_logging.logger import App_Logger
# from ..application_logging.logger import App_Logger
from ..application_logging.logger import App_Logger
import os
import glob
import openai
import pickle
import numpy as np
import pickle
from dotenv import load_dotenv
from qdrant_client.http.models import Batch, PointStruct
from qdrant_client import QdrantClient, models
from src.data_parsing.structured_text_extraction import PDFDocument
import json


load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = os.getenv("ROOT_PEM_FILE") #Download root.pem from this page and pass it to your code.
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY") #Personalized secured tokenID
openai.api_base = os.getenv("OPENAI_API_BASE") #LLM Gateway designated baseurl.pass the URL as it is.


#self.manger_pdf = "manager handbook policy in legato.pdf"
class GetAndStroreData:
    
    """ 
    This is a Python Class called GetAndStroreData .It is designed to get the all text from PDF , do the chunkings of text 
    and finally do the embedding and store the embedding in sqlite db in desired path.It has 4 instances 1.file_object for logs
    2. db_path for storing embeddings 3.db_name in which db or folder location we are storing the embedding lite.
    4.source_path is for where to get the pdf file.
    
    Written By : Data Science HR Usecase Team
    Version : 1.0
    Revisions : None
        
    """
    
    def __init__(self,db_name) -> None:  

        # self.list_pdf_docs = glob.glob("./source_files/*.pdf")
        self.file_object = open("./logs.txt","a+")
        self.db_path = './vector_store/'
        self.db_name = db_name
        self.source_path = f'./source_files/{self.db_name}/'
        self.logger = App_Logger()
    

    def document_chunks(self):
        """
        Method Name : document_chunks
        Description : This method returns all text chunks in list from the json text we got from structured_text_extraction file.
        OutPut : Text Docs
        On Failure: Log the exception in logs
            
        """
        try:
            self.logger.log(self.file_object,"Starting in document_chunks method in data_parsing file......")
            
            # Get the path of the folder containing the PDF files
            pdf_folder = os.path.join("./source_files/", self.db_name)

            # Get a list of all the PDF files in that folder
            pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf")) 
            # print(pdf_files)
            if pdf_files:
                # Choose the first PDF file in the list
                pdf_path = pdf_files[0]


            json_text = PDFDocument(pdf_path).extract_data()
            # json_text = json.dumps(json_data)
            
            # text_splitter = RecursiveCharacterTextSplitter(
            #     # Set a really small chunk size, just to show.
            #     chunk_size = 1500,
            #     chunk_overlap  = 200,
            #     length_function = len,
            #     add_start_index = True,
            # )
            # doc_chunks = text_splitter.create_documents([json_text])


            heading = ''
            subheading = ''
            chunks_list = []
            points = []
            count = 0
            for page in json_text['data']:
                for content in page:
                    if 'Heading' in content.keys():
                        heading = content['Heading']
                    if 'Sub_heading' in content.keys():
                        subheading = content['Sub_heading']
                    if 'Paragraph' in content.keys():
                        para = content['Paragraph']
                        overlap = ''
                        for char in range(0,len(para),1500):
                           
                            chunk = overlap
                            chunk += para[char:char+1500]

                            full_chunk = f'Heading = {heading}, Subheading = {subheading}, Content = {chunk}'

                            chunks_list.append(full_chunk)

                            # chunk_embedding = openai.Embedding.create(
                            #     model = "text-embedding-ada-002", input = full_chunk)['data'][0]['embedding']
                            # points.append(PointStruct(id = count, vector=chunk_embedding, payload={
                            #     "text": full_chunk, "heading": heading, "subheading": subheading}))
                            count += 1
                            overlap = chunk[-200:]

            return chunks_list

        except Exception as err:
            self.logger.log(self.file_object,f"Error in document_chunks in data_parsing file : {repr(err)}")

    def create_doc_embeddings(self):
        """
        Method Name : create_doc_embeddings
        Description : This method creates Embeddings from all Text Docs we got from document_chunks method and stores it in Qdradrant SQLite in db_Path/db_name .
        OutPut : Stores Embedding in Qdrant Sqlite
        On Failure: Log the exception in logs
            
        """
        try:
            self.logger.log(self.file_object,"Starting in create_doc_embeddings method in data_parsing file......")

            # self.document_chunks = self.document_chunks()


            doc_texts = self.document_chunks()
            # print(doc_texts)
            # print(doc_texts)
            openai_embeddings = []
            for doc in doc_texts:
                openai_embeddings.append(openai.Embedding.create(model = "text-embedding-ada-002", input = doc))

            embeddings_array = np.array([openai_embeddings[i]['data'][0]['embedding'] for i in range(len(doc_texts))])

            qdrant_client = QdrantClient(path=self.db_path)

            points = [] # map between docs and their embeddings
            for i, chunk in enumerate(doc_texts):
                # points.append(PointStruct(id=i, vector=embeddings_array[i], payload={"text": chunk}))
                points.append(PointStruct(id = i, vector=embeddings_array[i], payload={
                    "text": chunk}))
            
            qdrant_client.recreate_collection(
                collection_name=self.db_name,
                vectors_config=models.VectorParams(size=embeddings_array.shape[1], distance=models.Distance.COSINE),
            )

            qdrant_client.upsert(
                collection_name=self.db_name,
                wait=True,
                points=points
            )

            self.logger.log(self.file_object,"Successfully created Embeddings in quadrant db sqlite in create_doc_embeddings method in embedding file..Ending of Data Parsing Event..")
        except Exception as err:
            self.logger.log(self.file_object,f"Error in create_doc_embeddings method in data_parsing file: {repr(err)} ")
   
       
# if __name__=="__main__":
#     print("Running data parsing service")
#     GetAndStroreData("Manager_Handbook").create_doc_embeddings()
    