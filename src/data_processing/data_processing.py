import openai
import json
# from qdrantdb import QdrantEmbedding
from qdrant_client.http.models import Batch, PointStruct
from qdrant_client import QdrantClient, models
import pickle
# from data_parsing import GetAndStroreData
import os
# from logger.logger import log
# from logger.logger import log
from ..application_logging import logger
import pickle
from dotenv import load_dotenv
from qdrant_client.http.models import Batch, PointStruct
from qdrant_client import QdrantClient, models

load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = os.getenv("ROOT_PEM_FILE") #Download root.pem from this page and pass it to your code.
openai.api_key = os.getenv("OPENAI_API_KEY") #Personalized secured tokenID
openai.api_base = os.getenv("OPENAI_API_BASE") #LLM Gateway designated baseurl.pass the URL as it is.


class GetManagerBotResponse:
    
    """ 
    This is a Python Class called GetManagerBotResponse .It is designed to connect to embeddingdb get similar docs and give the response using GPT model.
    It has 3 instances 
    1. file_object for logs
    2. db_path to connect embeddings 
    3. db_name in which db or folder location we are storing the embedding lite.
    
    
    Written By : Data Science HR Usecase Team
    Version : 1.0
    Revisions : None
        
    """
    
    def __init__(self,db_name) -> None:
        self.file_object = open("./logs.txt","a+")
        self.db_path = './vector_store/'
        self.db_name = db_name
        self.logger = logger.App_Logger()
   
    def get_similar_docs(self,question):
        
        """
        Method Name : get_similar_docs
        Description : This method helps to find out the similar documents .
        input:
        OutPut : Similar documents
        On Failure: Log the exception in logs
            
        """
        try:    
            self.logger.log(self.file_object,"Starting in get_similar_docs method in data_processing file......")
            search_vector = openai.Embedding.create(model = "text-embedding-ada-002", input = question)['data'][0]['embedding']
            qdrant_client = QdrantClient(path=self.db_path)
            
            # embedding_path = self.db_path + os.listdir(self.db_path)[0]
            # with open(embedding_path,'rb') as f:
            #     qdrant_client = pickle.load(f)

            # similarity search to get the relevant documents
            search_result = qdrant_client.search(
                collection_name=self.db_name,
                query_vector=search_vector,
                limit=5
            )
            similar_docs = [search.payload['text'] for search in search_result]
            
            return similar_docs
        
        except Exception as err:
            
            self.logger.log(self.file_object,f"Error in get_similar_docs method in data_processing file: {repr(err)} ")


    def get_completion_from_messages(self,question,model="gpt3", temperature=0):
        """
        Method Name : get_completion_from_messages
        Description : This method give response using GPT model and prompts  .
        OutPut : Chat bot json response
        On Failure: Log the exception in logs
            
        """
        
        try:
            self.logger.log(self.file_object,"Starting in get_completion_from_messages method in data_processing file......")

            similar_docs = self.get_similar_docs(question)
            
            # similar_docs_text = " "
            # for doc in similar_docs:
            #     similar_docs_text += doc
            
            # similar_docs_text = " ".join(similar_docs)
            similar_docs_text = "{"+"} {".join(similar_docs)+"}"
            # self.logger.log(self.file_object,f"similardocs :  {similar_docs_text} ")
            message = [
            {'role':'system', 'content': """You are a Manager Assistant who will help manager to get answer from relevant context provided.
               The context given by system contains relevant search results in separate curly braces of the user's question.
                Use the following pieces of context to answer the question at the end.Include all relevant details from the context.
                
                If you don't know the answer, just say that you don't know, don't try to make up an answer.
                   
                context: """+similar_docs_text
            },
            {'role':'user', 'content': question}
                        ]
            response = openai.ChatCompletion.create(
                model=model,
                messages=message,
                temperature=temperature, # this is the degree of randomness of the model's output
            )
            response = json.loads(response)
            response = response['choices'][0]['message']['content']
            self.logger.log(self.file_object,"Successfully exceuted in get_completion_from_messages method in data_processing file......")
            result = {
                "status" : True,
                "message" : response
                    }
            return result
        except Exception as err:
            
            # print(err)
            self.logger.log(self.file_object,f"Error occured in get_completion_from_messages method in data_processing file: {repr(err)} ")
            result = {
                "status" : False,
                "message" : "Unable to get response from Bot"
                    }
            return result
            # raise err


# if __name__=="__main__":
#     # print(GetManagerBotResponse("Employee_Buddy").get_completion_from_messages("tell me about estimated time traveling UP to 20 km?"))
#     print(GetManagerBotResponse("Manager_Handbook").get_completion_from_messages(" What are the unwelcome acts for considering Sexual Harassment?"))
